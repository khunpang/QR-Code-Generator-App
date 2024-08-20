from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    qrcode_histories = relationship("QRCodeHistory", back_populates="owner")

class QRCodeHistory(Base):
    __tablename__ = 'qr_code_histories'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    qr_code_image_filename = Column(String)
    qr_code_image_base64 = Column(Text)  # เพิ่มฟิลด์สำหรับ Base64
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="qrcode_histories")
