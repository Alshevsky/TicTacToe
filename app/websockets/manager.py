from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException

from app.cache.game_cache import local_game_cache
from app.cache.ws_cache import WebSocketConnectionsCache


class WebsocketConnectionManager:
    def __init__(self):
        self.cache = WebSocketConnectionsCache()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


websockets_manager = WebsocketConnectionManager()
