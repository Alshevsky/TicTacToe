from dataclasses import dataclass
from enum import Enum
from uuid import UUID, uuid4

from fastapi.websockets import WebSocket


class GameItems(str, Enum):
    X = "X"
    O = "O"


class WebSocketActions(str, Enum):
    MAIN = "openedMain"
    CREATE = "create"
    JOIN = "join"
    UPDATE_GAME_LIST = "updateGameList"
    CLOSE_GAME = "close"
    SET_ITEM = "setItem"
    ERROR = "error"


class ErrorMessageTheme(str, Enum):
    WARNING = "warning"
    ERROR = "danger"
    INFO = "info"
    SUCCESS = "success"
    DEFAULT = "default"


@dataclass
class WebSocketConnectionState:
    in_game: bool
    player_uid: str
    websocket_connection: WebSocket


def is_valid_uuid(uid: str) -> bool:
    try:
        UUID(uid)
        return True
    except ValueError:
        return False


def gen_hexadecimal_uuid() -> str:
    """Create new hexadecimal UUID.

    Returns:
        str
    """
    return uuid4().hex
