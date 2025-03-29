import orjson
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.schemas.game import Game, GameRead
from app.settings import settings

redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

class RedisManager:
    def __init__(self):
        self.redis = redis
        self.pubsub = None

    async def get_redis(self):
        return self.redis

    async def get_redis_channel(self):
        if not self.pubsub:
            self.pubsub = self.redis.pubsub()
        return self.pubsub

    async def subscribe_to_channel(self, channel: str):
        pubsub = await self.get_redis_channel()
        await pubsub.subscribe(channel)

    async def unsubscribe_from_channel(self, channel: str):
        if self.pubsub:
            await self.pubsub.unsubscribe(channel)

    async def publish_to_channel(self, channel: str, message: str):
        await self.redis.publish(channel, message)

    async def get_message(self):
        if not self.pubsub:
            return None
        message = await self.pubsub.get_message(ignore_subscribe_messages=True)
        return orjson.loads(message["data"]) if message else None


class RedisCache:
    def __init__(self) -> None:
        self.redis = redis
    
    async def set(self, game_id: str, game: Game) -> None:
        try:
            await self.redis.set(game_id, orjson.dumps(game.dump()).decode("utf-8"), ex=60 * 60 * 24)
        except (RedisError, ValueError) as e:
            raise ValueError(f"Failed to save game to Redis: {e}")

    async def get(self, game_id: str) -> Game | None:
        try:
            if (data := await self.redis.get(game_id)) is None:
                return None
            return Game.load(orjson.loads(data))
        except (RedisError, ValueError) as e:
            raise ValueError(f"Failed to load game from Redis: {e}")

    async def delete(self, game_id: str) -> None:
        try:
            await self.redis.delete(game_id)
        except RedisError as e:
            raise ValueError(f"Failed to delete game from Redis: {e}")

    async def get_active_games(self) -> list[GameRead]:
        try:
            keys = await self.redis.keys("*")
            return [game for data in await self.redis.mget(keys) if (game := Game.to_read(orjson.loads(data))) and game.isActive]
        except (RedisError, ValueError) as e:
            raise ValueError(f"Failed to get all games from Redis: {e}")
