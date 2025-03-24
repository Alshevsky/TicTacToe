from uuid import uuid4

from fastapi.websockets import WebSocket
from pydantic import BaseModel

from app.helpers import GameItems
from app.websockets.manager import WebsocketConnectionManager
from database.models import User

from .player import Player


class GameListRead(BaseModel):
    gamesList: list
    userName: str


class GameCreate(BaseModel):
    gameName: str
    currentPlayerItem: GameItems


class Game:
    id: str = ""
    name: str = ""
    first_player: Player
    second_player: Player | None = None
    is_active: bool = False
    # Is the game currently active
    _player_turn: GameItems = GameItems.X
    _available_indexes: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    _win_patterns: list[list[int]] = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ]

    def __init__(self, user: User, game_name: str, user_item: GameItems | None = GameItems.X):
        self.id = f"{uuid4()}"
        self.name = game_name

        self._first_player_item = user_item
        self._second_player_item = GameItems.O if user_item == GameItems.X else GameItems.X

        player = Player(id=user.id, username=user.username, item=self._first_player_item)
        self.first_player = player

        self.game_state = dict().fromkeys(self._available_indexes, "")
        self.players_state: dict[str, Player] = {user.id: player}

        self.websocket_manager = WebsocketConnectionManager()

    @classmethod
    def create(cls, user: User, game_data: GameCreate) -> "Game":
        return cls(user, game_data.gameName, game_data.currentPlayerItem)

    async def join_player(self, user: User) -> bool:
        if self.is_active or self.second_player or user is None or self.first_player.id == user.id:
            return False
        player = Player(id=user.id, username=user.username, item=self._first_player_item)
        self.second_player = player
        self.players_state[user.id] = player
        self.is_active = True
        return True

    async def player_set_item(self, user: User, cell_index: int) -> GameItems:
        player = self.players_state.get(user.id)
        assert player is None, "Данный пользователь не имеет права устанавливать значения"
        assert player.item == self._player_turn, "Ход разрешен другому игроку"
        assert cell_index in self._available_indexes, "Передано неверное значение ячейки"
        assert self.game_state[cell_index] == "", "Попытка поставить значение, в уже занятую ячейку"
        self.game_state[cell_index] = player.item
        current_values = [set_item[0] for set_item in self.game_state.items() if set_item[1] == player.item]
        if len(current_values) >= 3:
            if current_values in self._win_patterns:
                print("Игрок выйграл")
            elif not list(filter(lambda x: self.game_state[x] == "", self.game_state)):
                print("Ничья, игра закончена")
        match player.item:
            case GameItems.X:
                self._player_turn = GameItems.O
            case GameItems.O:
                self._player_turn = GameItems.X
        return player.item

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "gameName": self.name,
            "currentPlayerName": self.first_player.username,
            "secondPlayerName": self.second_player.username if self.second_player else None,
            "currentPlayerItem": self.first_player.item.value,
            "secondPlayerItem": self.second_player.item.value if self.second_player else None,
        }
