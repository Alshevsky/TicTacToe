from dataclasses import dataclass

from fastapi.websockets import WebSocket

from app.helpers import GameItems


@dataclass
class Player:
    id: str
    username: str
    item: GameItems
    ws: WebSocket | None = None
