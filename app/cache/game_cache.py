import logging
import orjson
from redis.asyncio import Redis
from sqlalchemy import delete

from app.exceptions import GameIsNotCreated
from app.helpers import is_valid_uuid
from app.schemas import Game, GameCreate
from app.schemas.game import GameRead
from database.models import User
from app.cache.redis import RedisCache, RedisManager
from app.settings import settings
from app.websockets.helper import WebsocketMessageType
logger = logging.getLogger(__name__)


class GamesCacheManager:
    error_message = "Incorrect data has been transmitted, it is necessary to transfer the instance of `Game` class"
    _redis_cache = RedisCache()
    _redis_manager = RedisManager()
    
    def __init__(self):
        self._user_has_game = set()
    
    async def get(self, game_id: str) -> Game | None:
        try:
            return await self._redis_cache.get(game_id)
        except Exception as e:
            logger.error("Failed to get game: %s", e, exc_info=True)
            return None

    async def close_game(self, uid: str, user_id: str) -> bool:
        try:
            game: Game | None = await self._redis_cache.get(uid)
            if game is None or game.first_player.id != user_id:
                return False
            await self._redis_cache.delete(uid)
            self._user_has_game.remove(game.first_player.id)
            await self._redis_manager.publish_to_channel(
                channel=settings.REDIS_CHANNEL, 
                message=orjson.dumps({"type": WebsocketMessageType.GAME_DELETED, "gameId": uid})
            )
            return True
        except Exception as e:
            logger.error("Failed to close game: %s", e, exc_info=True)
            return False

    async def create_game(self, user: User, game_data: GameCreate) -> Game:
        try:
            if user is not None and user.id in self._user_has_game:
                raise GameIsNotCreated("You already have a game created")
            game = Game.create(user, game_data)
            await self._redis_cache.set(game.id, game)
            self._user_has_game.add(user.id)
            await self._redis_manager.publish_to_channel(
                channel=settings.REDIS_CHANNEL, 
                message=orjson.dumps({"type": WebsocketMessageType.GAME_ADDED, "game": game.dump_model_json()})
            )
            return game
        except Exception as e:
            logger.error("Failed to create game: %s", e, exc_info=True)
            raise GameIsNotCreated("Failed to create game")

    async def join_game(self, user: User, game_id: str):
        try:
            game: Game | None = await self._redis_cache.get(game_id)
            if game is None or not game.is_active:
                raise GameIsNotCreated("Game not found")
            if game.first_player.id == user.id:
                raise GameIsNotCreated("You are the creator of the game")
            await game.join_player(user)
            await self._redis_cache.set(game_id, game)
            await self._redis_manager.publish_to_channel(
                channel=settings.REDIS_CHANNEL, 
                message=orjson.dumps({"type": WebsocketMessageType.GAME_JOINED, "gameId": game.model_dump()})
            )
            return game.second_player.item
        except GameIsNotCreated as e:
            raise e
        except Exception as e:
            logger.error("Failed to join game: %s", e, exc_info=True)
            raise GameIsNotCreated("Failed to join game")

    async def get_games_info_data(self) -> list[GameRead]:
        return await self._redis_cache.get_active_games()


game_cache_manager = GamesCacheManager()
