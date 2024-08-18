from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreate
from .auth import pwd_context

# ฟังก์ชันค้นหาผู้ใช้ตามชื่อผู้ใช้
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# ฟังก์ชันสร้างผู้ใช้ใหม่
def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)  # Hash รหัสผ่าน
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)  # เพิ่มผู้ใช้ใหม่ในฐานข้อมูล
    db.commit()  # บันทึกการเปลี่ยนแปลง
    return db_user
