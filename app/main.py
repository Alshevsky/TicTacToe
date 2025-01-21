from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import router
from database import create_db_and_tables
from app.settings import settings

import logging.config


logger = logging.getLogger(__name__)

logger.info("Starting FastAPI")
logger.info("VERSION - %s", settings.PROJECT_VERSION)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION, debug=settings.DEBUG, lifespan=lifespan)

app.include_router(router=router)
