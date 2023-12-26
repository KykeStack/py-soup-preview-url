from typing import Annotated, List
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError
from schemas.token import TokenPayload

from core.config import settings
from pydantic import ValidationError

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

def validate_domain(domain: str) -> bool:
    domains: List[str] = [str(origin) for origin in settings.CLIENT_DOMAINS]
    if domain not in domains: 
        False
        
    return True

def get_token_payload(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as error:
        print("Error: ", error)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return token_data

async def get_access(token: Annotated[str, Depends(reusable_oauth2)]) -> None:
    oauth_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
    try:
        payload = get_token_payload(token)
        if not payload.sub or not validate_domain(payload.sub):
            raise oauth_exception
    except Exception as error:
        raise oauth_exception

if __name__ == "__main__":
    ...