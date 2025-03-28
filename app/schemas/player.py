from dataclasses import dataclass

from app.helpers import GameItems


@dataclass
class Player:
    id: str
    username: str
    item: GameItems
    
    def dump(self) -> dict:
        return {
            "id": f"{self.id}",
            "username": self.username,
            "item": self.item.value
        }
    
    def to_dict(self) -> dict:
        return self.dump()

    @classmethod
    def load(cls, data: dict) -> "Player":
        return cls(
            id=data["id"],
            username=data["username"],
            item=GameItems(data["item"])
        )
