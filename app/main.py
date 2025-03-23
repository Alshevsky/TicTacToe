import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import router
from app.auth.websocket_auth import JWTWebsocketAuth
from app.settings import settings
from database import create_db_and_tables

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


@app.websocket("/games/{game_id}/ws")
async def websocket_game_endpoint(game_id: str, websocket: WebSocket):
    await websocket.accept()
    # game = local_game_cache["game_id"]
    await websocket.send_json({"type": "auth"})
    token_message = await websocket.receive_json()
    print(token_message)
    user = JWTWebsocketAuth.validate(token_message['token'])
    print(user)
    while True:
        data = await websocket.receive_text()
        await websocket.send_json({"chatMessage": data})
