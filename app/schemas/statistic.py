from pydantic import BaseModel, Field

from app.schemas import Player


class PlayerStatistic(BaseModel):
    player: Player
    game_played: int = 0
    game_win: int = 0


class UserStatisticRead(BaseModel):
    games_total: int = Field(default=0, serialize_alias="gamesPlayed")
    games_win: int = Field(default=0, serialize_alias="gamesWin")
    games_loose: int = Field(default=0, serialize_alias="gamesLoose")

    class Config:
        from_attributes = True
