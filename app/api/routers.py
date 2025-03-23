from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.games import router as main_router
from app.settings import settings

router = APIRouter(prefix=settings.API_PREFIX)

router.include_router(main_router)
router.include_router(auth_router)
