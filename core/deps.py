from typing import Annotated, List
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

from schemas.token import TokenPayload
from schemas.functions import FunctionStatus

from core.config import settings

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

def validate_domain(domain: str):
    domains: List[str] = [str(origin) for origin in settings.CLIENT_DOMAINS]
    if len(domains) < 1: return False
    if domain not in domains: False
    return True

def get_token_payload(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        token_data = TokenPayload(**payload)
    except Exception as e:
        print("JWT Error", e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return token_data

async def get_access(token: Annotated[str, Depends(reusable_oauth2)]) -> FunctionStatus:
    try:
        payload = get_token_payload(token)
        if payload.sub == None:
            return FunctionStatus(status=False, section=0, error=f"Afther jwt.decode found Security Issues", functionName='get_access')
            
        if not validate_domain(payload.sub):
            return FunctionStatus(status=False, section=1, error='Invalid domain', functionName='get_access')
          
        return FunctionStatus(status=True, section=2, functionName='get_access')
    except Exception as error:
        return FunctionStatus(status=False, section=3, error=error, functionName='get_access')

if __name__ == "__main__":
    ...