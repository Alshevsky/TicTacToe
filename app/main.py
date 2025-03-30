import asyncio
import logging.config
from contextlib import asynccontextmanager
from typing import Any

import orjson
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, WebSocketException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketState

from app.api.routers import router
from app.auth.websocket_auth import JWTWebsocketAuth
from app.cache.game_cache import game_cache_manager
from app.cache.redis import RedisManager
from app.operations.statistic import get_statistic
from app.operations.users import get_user_and_statistic_by_username
from app.settings import settings
from app.websockets.helper import WebsocketMessageType
from database import create_db_and_tables
from database.models.users import User

logger = logging.getLogger(__name__)

logger.info("Starting FastAPI")
logger.info("VERSION - %s", settings.PROJECT_VERSION)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION, debug=settings.DEBUG, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router=router)


async def auth_user(websocket: WebSocket) -> None | User:
    try:
        # Ждем сообщение с токеном
        token_message = await websocket.receive_json()
        if not isinstance(token_message, dict) or "token" not in token_message:
            await websocket.send_json({"type": "auth", "status": "error", "message": "Токен не предоставлен"})
            return None

        user = await JWTWebsocketAuth.validate(token_message["token"])
        if user:
            await websocket.send_json(
                {"type": "auth", "status": "success", "user": {"id": str(user.id), "username": user.username}}
            )
            return user
        else:
            await websocket.send_json({"type": "auth", "status": "error", "message": "Недействительный токен"})
            return None
    except WebSocketException as e:
        logger.error(f"WebSocket exception: {e}")
        return None
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    redis_manager = RedisManager()
    user = None

    try:
        # Аутентифицируем пользователя
        user = await auth_user(websocket)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Подписываемся на канал
        await redis_manager.subscribe_to_channel(settings.REDIS_CHANNEL)

        while True:
            try:
                # Создаем задачи для параллельной обработки сообщений
                websocket_task = asyncio.create_task(websocket.receive_json())
                redis_task = asyncio.create_task(redis_manager.get_message())

                # Ждем первое завершившееся событие
                done, pending = await asyncio.wait([websocket_task, redis_task], return_when=asyncio.FIRST_COMPLETED)

                # Отменяем оставшиеся задачи
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                # Обрабатываем результат
                for task in done:
                    try:
                        result = task.result()
                        if result is None:
                            continue

                        if isinstance(result, dict) and "type" in result:
                            # Определяем источник сообщения по задаче
                            if task == websocket_task:
                                await handle_websocket_message(result, user, redis_manager, websocket)
                            else:
                                await handle_redis_message(result, user, websocket)
                    except WebSocketDisconnect:
                        raise
                    except asyncio.CancelledError:
                        logger.info("Task cancelled")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")

            except WebSocketDisconnect:
                logger.info("WebSocket disconnected normally")
                break
            except Exception as e:
                logger.error(f"Error in message processing loop: {e}")
                break

    except WebSocketException as e:
        logger.error(f"WebSocket exception: {e}")
    except WebSocketDisconnect as e:
        logger.debug("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        try:
            await redis_manager.unsubscribe_from_channel(settings.REDIS_CHANNEL)
            if websocket.state != WebSocketState.DISCONNECTED:
                await websocket.close()
        except Exception as e:
            logger.error(f"Error in cleanup: {e}")


async def handle_websocket_message(
    data: dict, user: User | None, redis_manager: RedisManager, websocket: WebSocket
) -> None:
    try:
        match data["type"]:
            case WebsocketMessageType.GAME_INVITE:
                statistic = await get_statistic(user.id)
                data["stats"] = statistic.model_dump()
                await redis_manager.publish_to_channel(settings.REDIS_CHANNEL, orjson.dumps(data))
            case WebsocketMessageType.GAME_JOINED:
                await websocket.send_json(data)
            case WebsocketMessageType.GAME_ENDED:
                await websocket.send_json(data)
            case WebsocketMessageType.GAME_WIN:
                await websocket.send_json(data)
            case "auth":
                user = await JWTWebsocketAuth.validate(data["token"])
            case _:
                logger.warning(f"Unknown WebSocket message type received: {data['type']}")
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")


async def handle_redis_message(data: dict, user: User | None, websocket: WebSocket) -> None:
    try:
        match data["type"]:
            case WebsocketMessageType.GAME_INVITE:
                if user is None:
                    logger.warning("Received Redis message for unauthenticated user")
                    return
                if user.username != data.get("targetPlayer"):
                    return
                await websocket.send_json(data)
            case _:
                await websocket.send_json(data)
                logger.warning(f"Unknown Redis message type received: {data['type']}")
    except Exception as e:
        logger.error(f"Error handling Redis message: {e}")
        # if websocket.state != WebSocketState.DISCONNECTED:
        #     await websocket.close()


@app.websocket("/games/{game_id}/ws")
async def websocket_game_endpoint(game_id: str, websocket: WebSocket) -> None:
    """
    WebSocket endpoint для игровой сессии.

    Args:
        game_id: Идентификатор игры
        websocket: WebSocket соединение

    Raises:
        WebSocketDisconnect: При разрыве соединения
        ConnectionClosed: При закрытии соединения
    """
    if (game := game_cache_manager.get(game_id)) is None:
        await websocket.send_json({"type": "Error", "message": "Game not found"})
        await websocket.close()
        return

    await websocket.accept()
    await websocket.send_json({"type": "auth"})

    try:
        token_message = await websocket.receive_json()
        user = await JWTWebsocketAuth.validate(token_message["token"])
        websocket_manager = game.websocket_manager
        await websocket_manager.add(user, websocket=websocket)

        while True:
            try:
                data: dict[str, Any] = await websocket.receive_json()
                if not isinstance(data, dict) or "type" not in data:
                    logger.warning(f"Invalid message format received: {data}")
                    continue

                match data["type"]:
                    case "sendChatMessage":
                        data["type"] = "chatMessage"
                        await websocket_manager.broadcast_json(data)
                    case "makeMove":
                        game_state = await game.player_set_item(user, data["cellIndex"])
                        data["type"] = "gameState"
                        data["gameState"] = game_state.to_dict()
                        await websocket_manager.broadcast_json(data)
                    case "closeGame":
                        game_cache_manager.close_game(game_id)
                        await websocket.close()
                        break
                    case _:
                        logger.warning(f"Unknown message type received: {data['type']}")

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user {user}")
                await websocket_manager.remove(user)
                if not websocket_manager.active_connections:
                    game_cache_manager.close_game(game_id)
                break

    except Exception as e:
        logger.error(f"Authentication or connection error: {e}")
        await websocket.close()
        return
