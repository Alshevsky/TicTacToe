from app.helpers import is_valid_uuid
from app.schemas import Game


class GamesListCache:
    data: dict[str, Game] = {}
    error_message = "Incorrect data has been transmitted, it is necessary to transfer the instance of `Game` class"

    def __setitem__(self, key, item: Game) -> None:
        assert isinstance(item, Game), self.error_message
        assert is_valid_uuid(key), "Incorrect uid format"
        self.data[key] = item

    def __getitem__(self, game_id: str) -> Game | None:
        return self.data[game_id]

    def __delitem__(self, game_id: str):
        del self.data[game_id]

    def __contains__(self, game_id: str) -> bool:
        return game_id in self.data

    def __iter__(self):
        return iter(self.data)

    def pop(self, game_id: str, default=None) -> Game | None:
        return self.data.pop(game_id, default)

    def get_games_info_data(self) -> list[dict]:
        return [game.to_dict() for game in self.data.values() if not game.is_active]

    def game_is_waiting_players_count(self) -> int:
        return len([game for game in self.data.values() if not game.is_active])


local_game_cache = GamesListCache()
