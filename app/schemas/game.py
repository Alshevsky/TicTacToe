from uuid import uuid4

from fastapi.websockets import WebSocket

from app.exceptions import GameIsNotCreated
from app.helpers import GameItems

from .player import Player


class Game:
    id: str = f"{uuid4()}"
    first_player: Player
    second_player: Player | None = None
    is_active: bool = False  # Is the game currently active
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

    def __init__(self, player: Player):
        self.first_player = player
        self.first_player.item = GameItems.X
        self._id = f"{uuid4()}"
        self.game_state = dict().fromkeys(self._available_indexes, "")
        super().__init__()

    @classmethod
    async def create(cls, player: Player) -> "Game":
        if player is None or len(player.created_games) >= 1:
            raise GameIsNotCreated("You already have a game created")
        created_game = cls(player)
        player.created_games.append(created_game.uid)
        return created_game

    async def join_player(self, player: Player) -> bool:
        if self.is_active or self.second_player or player is None or self.first_player == player:
            return False
        item = GameItems.O if self.first_player.item == GameItems.X else GameItems.X
        player.item = item
        self.second_player = player
        self.is_active = True
        return True

    async def close(self):
        self.first_player.created_games.clear()

    async def get_users_ws(self) -> list[WebSocket]:
        users_ws = []
        if not self.first_player or not self.second_player:
            return users_ws
        users_ws += [self.first_player.web_socket, self.second_player.web_socket]
        return users_ws

    async def player_set_item(self, player: Player, cell_index: int) -> GameItems:
        assert player in [self.first_player, self.second_player], (
            "Данный пользователь не имеет права устанавливать " "значения"
        )
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
            "id": self._id,
            "isActive": self.is_active,
            "currentPlayerName": self.first_player.name,
            "secondPlayerName": self.second_player.name if self.second_player else None,
            "currentPlayerItem": self.first_player.item.value,
            "secondPlayerItem": self.second_player.item.value if self.second_player else None,
        }
