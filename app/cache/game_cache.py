from redis.asyncio import Redis

from app.exceptions import GameIsNotCreated
from app.helpers import is_valid_uuid
from app.schemas import Game, GameCreate
from database.models import User


class GamesListCache:
    data: dict[str, Game] = {}
    user_mapping: dict[str, str] = {}
    error_message = "Incorrect data has been transmitted, it is necessary to transfer the instance of `Game` class"

    def __setitem__(self, key, item: Game) -> None:
        assert isinstance(item, Game), self.error_message
        self.data[key] = item
        self.user_mapping[item.first_player.id] = key

    def __getitem__(self, game_id: str) -> Game | None:
        return self.data[game_id]

    def __delitem__(self, game_id: str):
        del self.data[game_id]

    def __contains__(self, game_id: str) -> bool:
        return game_id in self.data

    def __iter__(self):
        return iter(self.data)
    
    def get(self, game_id: str) -> Game | None:
        return self.data.get(game_id)

    def close_game(self, uid: str) -> bool:
        if (game := self.data.pop(uid, None)) is None:
            return True
        self.user_mapping.pop(game.first_player.id)
        del game

    def create_game(self, user: User, game_data: GameCreate) -> Game:
        if user is not None and self.get_by_user_id(user.id):
            raise GameIsNotCreated("You already have a game created")
        elif user is None:
            raise ValueError("Player is None")
        game = Game.create(user, game_data)
        self.__setitem__(game.id, game)
        return game

    async def join_game(self, user: User, game_id: str):
        game = self.get(game_id)
        if game is None:
            raise GameIsNotCreated("Game not found")
        if game.first_player.id == user.id:
            raise GameIsNotCreated("You are the creator of the game")
        game.join_player(user)
        return game

    def get_by_user_id(self, uid: str) -> Game | None:
        return self.data.get(self.user_mapping.get(uid))

    def pop(self, game_id: str, default=None) -> Game | None:
        return self.data.pop(game_id, default)

    def get_games_info_data(self) -> list[dict]:
        print(self.data.values())
        return [game.to_dict() for game in self.data.values() if not game.is_active]

    def game_is_waiting_players_count(self) -> int:
        return len([game for game in self.data.values() if not game.is_active])


local_game_cache = GamesListCache()
