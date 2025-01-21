from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from app.api.auth import router as auth_router
from app.api.main import router as main_router
from settings import settings

router = APIRouter(prefix=settings.API_PREFIX)

router.include_router(main_router, dependencies=[Depends(HTTPBearer())])
router.include_router(auth_router)
