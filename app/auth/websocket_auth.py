from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.settings import settings


class JWTWebsocketAuth:
    def decode_jwt(token: str) -> dict | None:
        try:
            options = {'exp': True, 'verify_signature': True, 'verify_aud': False} 
            payload = jwt.decode(token, settings.SECRET, algorithms=settings.ALGORITHM, options=options)
            return payload
        except JWTError as e:
            return None
    @classmethod
    def validate(cls, token: str):
        scheme, _, param = token.partition(" ")
        credentials = HTTPAuthorizationCredentials(scheme=scheme, credentials=param)
        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid authentication scheme.')
        
        if decoded_jwt := cls.decode_jwt(credentials.credentials):
            pass
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid authorization code.')