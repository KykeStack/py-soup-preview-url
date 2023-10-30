from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt
from core.config import settings


def create_access_token(*, subject: Union[str, Any], expires_delta: timedelta = None, force_totp: bool = False, admin: Optional[bool] = False) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "totp": force_totp, "admin": admin}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

if settings.DEV_MODE:
    def create_access_token_dev(*, subject: Union[str, Any]) -> str:
        expire = datetime.utcnow() +  timedelta(weeks=1.0)
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

if __name__ == "__main__":
    ...