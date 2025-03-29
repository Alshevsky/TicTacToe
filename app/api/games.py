from fastapi import APIRouter, Depends, HTTPException, Response, WebSocket, status

from app import settings
from app.auth.user_manager import current_active_user
from app.cache.game_cache import game_cache_manager
from app.cache.redis import RedisManager
from app.operations.statistic import get_statistic
from app.schemas.game import GameRead
from app.websockets.helper import WebsocketMessageType
from app.exceptions import GameIsNotCreated
from app.schemas import GameCreate, GameListRead, GameJoin
from database.models import User

router = APIRouter(tags=["games"])


@router.get("/games")
async def main_page(user: User = Depends(current_active_user)) -> GameListRead:
    try:
        return GameListRead(gamesList=await game_cache_manager.get_games_info_data(), userName=user.username)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/games")
async def game_create(game_data: GameCreate, user: User = Depends(current_active_user)) -> GameRead:
    try:
        game = await game_cache_manager.create_game(user, game_data)
        return game.dump_model()
    except (GameIsNotCreated, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/games/{game_id}/join")
async def game_join(game_id: str, user: User = Depends(current_active_user)):
    try:
        await game_cache_manager.join_game(user)
        statistic = await get_statistic(user.id)
        await RedisManager.publish_message(settings.REDIS_CHANNEL, {"type": WebsocketMessageType.GAME_JOINED, "game_id": game_id, "current_player_item": user.item, "stats": statistic.to_dict()})
        return GameJoin(gameId=game_id, currentPlayerItem=user.item)
    except (GameIsNotCreated, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/games/{game_id}/end")
async def game_end(game_id: str, user: User = Depends(current_active_user)):
    try:
        game_removed = await game_cache_manager.close_game(game_id, user.id)
        if not game_removed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Game is not found or you are not the current player of this game")
        return Response(status_code=status.HTTP_200_OK)
    except (GameIsNotCreated, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
