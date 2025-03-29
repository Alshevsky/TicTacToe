from enum import Enum


class WebsocketMessageType(Enum):
    GAME_ADDED = "gameAdded"
    GAME_UPDATED = "gameUpdated"
    GAME_DELETED = "gameDeleted"
    GAME_JOINED = "gameJoined"
    GAME_LEFT = "gameLeft"
    GAME_STARTED = "gameStarted"
    GAME_ENDED = "gameEnded"
    GAME_WIN = "gameWin"
    GAME_INVITE = "gameInvite"