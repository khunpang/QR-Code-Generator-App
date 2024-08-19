from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
