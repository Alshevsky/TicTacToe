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

logger = logging.getLogger(__name__)

logger.info("Starting FastAPI")
logger.info("VERSION - %s", settings.PROJECT_VERSION)

redis_manager = RedisManager()


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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        await websocket.send_json({"type": "auth"})
        token_message = await websocket.receive_json()
        # await JWTWebsocketAuth.validate(token_message["token"])
        
        # Подписываемся на канал
        await redis_manager.subscribe_to_channel(settings.REDIS_CHANNEL)
        
        while True:
            # Проверяем сообщения из Redis
            if message := await redis_manager.get_message():
                await websocket.send_json(message)
            
            # Проверяем сообщения от клиента
            try:
                data = await websocket.receive_json()
                print(data)
            except WebSocketDisconnect:
                break
                
    except WebSocketException as e:
        logger.error(f"WebSocket exception: {e}")
    except WebSocketDisconnect:
        logger.debug("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await redis_manager.unsubscribe_from_channel("games_channel")
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
