from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.operations.users import get_user_by_id
from app.settings import settings
from database.models import User


class JWTWebsocketAuth:
    async def decode_jwt(token: str) -> dict | None:
        try:
            options = {"exp": True, "verify_signature": True, "verify_aud": False}
            payload = jwt.decode(token, settings.SECRET, algorithms=settings.ALGORITHM, options=options)
            return payload
        except JWTError:
            return None

    @classmethod
    async def validate(cls, token: str) -> User | None:
        scheme, _, param = token.partition(" ")
        credentials = HTTPAuthorizationCredentials(scheme=scheme, credentials=param)
        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")

        if decoded_jwt := await cls.decode_jwt(credentials.credentials):
            user = await get_user_by_id(decoded_jwt["sub"])
            return user
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization code.")
