from dataclasses import dataclass, asdict

from fastapi.websockets import WebSocket

from app.helpers import GameItems


@dataclass
class Player:
    id: str
    username: str
    item: GameItems
    
    def dump(self) -> dict:
        return asdict(self)
    
    def to_dict(self) -> dict:
        return self.dump()

    def load(self, data: dict) -> "Player":
        return Player(**data)
