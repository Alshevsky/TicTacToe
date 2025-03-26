from uuid import uuid4

from pydantic import BaseModel

from app.exceptions import GameIsNotCreated
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


class GameState(BaseModel):
    winner: str | None = None
    finished: bool = False


class Game:
    slots = (
        "id", "name", "first_player", "second_player", 
        "is_active", "_player_turn", "_available_indexes", 
        "_win_patterns", "_first_player_item", "_second_player_item",
        "game_state", "players_state", "websocket_manager"
    )
    
    id: str = ""
    name: str = ""
    first_player: Player
    second_player: Player | None = None
    is_active: bool = False
    # Is the game currently active
    _player_turn: GameItems = GameItems.X
    _available_indexes: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    _win_patterns: list[list[int, int, int]] = [
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
            raise GameIsNotCreated("Game is not active or user is already in the game")
        player = Player(id=user.id, username=user.username, item=self._first_player_item)
        self.second_player = player
        self.players_state[user.id] = player
        self.is_active = True
        return True

    async def player_set_item(self, user: User, cell_index: int) -> GameState:
        """Метод для установки значения в ячейку.

        Args:
            user (User): Пользователь, который делает ход
            cell_index (int): Индекс ячейки, в которую будет установлено значение

        Returns:
            GameState: ID следующего игрока, который выиграл или None, если игра не закончена
        """
        player = self.players_state.get(user.id)
        assert player is None, "Данный пользователь не имеет права устанавливать значения"
        assert player.item == self._player_turn, "Ход разрешен другому игроку"
        assert cell_index in self._available_indexes, "Передано неверное значение ячейки"
        assert self.game_state[cell_index] == "", "Попытка поставить значение, в уже занятую ячейку"

        finished: bool = False
        winner: str | None = None
        self.game_state[cell_index] = player.item
        current_values = [set_item[0] for set_item in self.game_state.items() if set_item[1] == player.item]

        if len(current_values) >= 3:
            if current_values in self._win_patterns:
                winner = player.id
                finished = True
            elif not list(filter(lambda x: self.game_state[x] == "", self.game_state)):
                finished = True

        self._player_turn = GameItems.O if self._player_turn == GameItems.X else GameItems.X
        return GameState(winner=winner, finished=finished)
    
    def dump(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "first_player": self.first_player.dump(),
            "second_player": self.second_player.dump() if self.second_player else None,
            "first_player_item": self._first_player_item,
            "is_active": self.is_active,
        }
    
    @classmethod
    def load(cls, data: dict) -> "Game":
        return cls(
            id=data["id"],
            name=data["name"],
            first_player=Player.load(data["first_player"]),
            second_player=Player.load(data["second_player"]) if data["second_player"] else None,
            _first_player_item=data["first_player_item"],
            _second_player_item=GameItems.O if data["first_player_item"] == GameItems.X else GameItems.X,
            is_active=data["is_active"],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "gameName": self.name,
            "currentPlayerName": self.first_player.username,
            "secondPlayerName": self.second_player.username if self.second_player else None,
            "currentPlayerItem": self.first_player.item.value,
            "secondPlayerItem": self.second_player.item.value if self.second_player else None,
        }
