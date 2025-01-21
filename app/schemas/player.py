from fastapi.websockets import WebSocket

from app.helpers import GameItems, gen_hexadecimal_uuid


class Player:
    id: str
    ws: WebSocket
    name: str
    item: GameItems = GameItems.X
    created_games: list[str] = []

    @property
    def web_socket(self) -> WebSocket:
        return self.ws
