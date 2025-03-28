from fastapi import APIRouter, Depends, HTTPException, WebSocket, status

from app.auth.user_manager import current_active_user
from app.cache.game_cache import game_cache_manager
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
async def game_create(game_data: GameCreate, user: User = Depends(current_active_user)) -> dict:
    try:
        game = await game_cache_manager.create_game(user, game_data)
        return game.to_dict()
    except (GameIsNotCreated, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/games/{game_id}/join")
async def game_join(game_id: str, user: User = Depends(current_active_user)):
    try:
        await game_cache_manager.join_game(user)
        return GameJoin(gameId=game_id, currentPlayerItem=user.item)
    except (GameIsNotCreated, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
