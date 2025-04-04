from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, status

from database.models import User


class WebsocketConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def add(self, user: User, websocket: WebSocket):
        if user.id in self.active_connections:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="User already connected")
        if len(self.active_connections) >= 2:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Too many connections")
        self.active_connections[user.id] = websocket

    async def disconnect(self, uid: str):
        websocket = self.active_connections.pop(uid)
        await websocket.close()

    async def send_personal_message(self, uid: str, message: str):
        websocket = self.active_connections[uid]
        await websocket.send_text(message)

    async def send_personal_json(self, uid: str, data: dict):
        websocket = self.active_connections[uid]
        await websocket.send_json(data)

    async def broadcast_message(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

    async def broadcast_json(self, data: dict):
        for connection in self.active_connections.values():
            await connection.send_json(data)
