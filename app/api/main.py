import orjson
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/")
async def main_page(request: Request) -> str:
    print(request.headers)
    return orjson.dumps({"user": "Hello World"}).decode()
