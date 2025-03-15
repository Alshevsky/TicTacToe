import orjson
from fastapi import APIRouter, Depends
from app.cache.game_cache import local_game_cache
from database.models import User
from app.auth.user_manager import current_active_user

router = APIRouter(tags=["main"])


@router.get("/")
async def main_page(user: User = Depends(current_active_user)) -> str:
    print(user.username)
    return orjson.dumps({"data": local_game_cache.get_games_info_data()}).decode()
