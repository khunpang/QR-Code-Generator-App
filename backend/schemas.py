from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class QRCodeHistoryCreate(BaseModel):
    text: str
    qr_code_image_filename: str
    qr_code_image_base64: str
    user_id: int
