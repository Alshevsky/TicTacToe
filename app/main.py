import asyncio
import logging.config
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import router
from app.auth.websocket_auth import JWTWebsocketAuth
from app.cache.game_cache import game_cache_manager
from app.settings import settings
from database import create_db_and_tables
from app.cache.redis import RedisManager
from database.models.users import User
from app.websockets.helper import WebsocketMessageType

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
        await websocket.send_json({"type": "auth"})
        token_message = await websocket.receive_json()
        user = await JWTWebsocketAuth.validate(token_message["token"])
        return user
    except WebSocketException as e:
        logger.error(f"WebSocket exception: {e}")
        return None


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    redis_manager = RedisManager()
    try:
        user = await auth_user(websocket)
        # Подписываемся на канал
        await redis_manager.subscribe_to_channel(settings.REDIS_CHANNEL)
        
        while True:
            # Проверяем сообщения из Redis
            data: dict[str, Any] = await websocket.receive_json()
            if isinstance(data, dict) and "type" in data:
                match data["type"]:
                    case WebsocketMessageType.GAME_INVITE:
                        if user is None:
                            if (user := await auth_user(websocket)) is None:
                                await websocket.close()
                                return
                        if user.username != data["targetPlayer"]:
                            continue
                        await websocket.send_json(data)
                    case WebsocketMessageType.GAME_JOINED:
                        data["type"] = WebsocketMessageType.GAME_INVITE
                        await redis_manager.publish_message(settings.REDIS_CHANNEL, data)
                        await websocket.send_json(data)
                    case WebsocketMessageType.GAME_ENDED:
                        await websocket.send_json(data)
                    case WebsocketMessageType.GAME_WIN:
                        await websocket.send_json(data)
                        
                    case _:
                        logger.warning(f"Unknown message type received: {data['type']}")
            if not (message := await redis_manager.get_message()):
                await asyncio.sleep(0.1)
                continue
            
            await websocket.send_json(message)
            
                
    except WebSocketException as e:
        logger.error(f"WebSocket exception: {e}")
    except WebSocketDisconnect:
        logger.debug("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await redis_manager.unsubscribe_from_channel(settings.REDIS_CHANNEL)
        await websocket.close()


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
