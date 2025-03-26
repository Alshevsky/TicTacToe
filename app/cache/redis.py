import orjson

from redis.asyncio import Redis

from app.settings import settings
from app.schemas.game import Game

redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

async def get_redis():
    return redis

async def get_redis_channel():
    return redis.pubsub()

async def subscribe_to_channel(channel: str):
    return await redis.subscribe(channel)

async def unsubscribe_from_channel(channel: str):
    return await redis.unsubscribe(channel)

async def publish_to_channel(channel: str, message: str):
    return await redis.publish(channel, message)

async def get_message_from_channel(channel: str):
    return await redis.get(channel)


class RedisCache:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def set(self, game_id: str, game: Game) -> None:
        await self.redis.set(game_id, orjson.dumps(game.dump()))

    async def get(self, game_id: str) -> Game | None:
        data = await self.redis.get(game_id)
        if (data := await self.redis.get(game_id)) is None:
            return None
        return Game.load(orjson.loads(data))

