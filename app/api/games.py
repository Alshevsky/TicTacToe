from fastapi import APIRouter, Depends, HTTPException, WebSocket, status

from app.auth.user_manager import current_active_user
from app.cache.game_cache import local_game_cache
from app.exceptions import GameIsNotCreated
from app.schemas import GameCreate, GameListRead
from database.models import User

router = APIRouter(tags=["games"])


@router.get("/games")
async def main_page(user: User = Depends(current_active_user)) -> GameListRead:
    return GameListRead(gamesList=local_game_cache.get_games_info_data(), userName=user.username)


@router.post("/games")
async def game_create(game_data: GameCreate, user: User = Depends(current_active_user)) -> dict:
    try:
        game = local_game_cache.create_game(user, game_data)
        return game.to_dict()
    except (GameIsNotCreated, ValueError) as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/games/{game_id}")
async def game_join(user: User = Depends(current_active_user)):
    try:
        local_game_cache.join_game(user)
    except (GameIsNotCreated, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
