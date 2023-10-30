from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None

if __name__ == "__main__":
    ...