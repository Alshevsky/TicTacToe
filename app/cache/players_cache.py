from app.helpers import is_valid_uuid
from app.schemas import Player


class PlayersListCache:
    data: dict[str, Player] = {}
    error_message = "Incorrect data has been transmitted, it is necessary to transfer the instance of `Game` class"

    def __setitem__(self, key, item: Player) -> None:
        assert isinstance(item, Player), self.error_message
        assert is_valid_uuid(key), "Incorrect uid format"
        self.data[key] = item

    def __getitem__(self, player_id: str) -> Player | None:
        return self.data[player_id]

    def __delitem__(self, player_id: str) -> None:
        del self.data[player_id]

    def __contains__(self, player_id: str) -> bool:
        return player_id in self.data

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def pop(self, player_id: str, default=None) -> Player | None:
        return self.data.pop(player_id, default)


local_player_cache = PlayersListCache()
