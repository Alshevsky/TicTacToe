from pydantic import BaseModel

from app.schemas import Player


class PlayerStatistic(BaseModel):
    player: Player
    game_played: int = 0
    game_win: int = 0
