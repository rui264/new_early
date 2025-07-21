#用户操作函数
from sqlalchemy.orm import Session
from .models import User ,History
from .security import get_password_hash, verify_password

def get_user_by_username(db: Session, user_name: str):
    return db.query(User).filter(User.user_name == user_name).first()

def create_user(db: Session, user_name: str, password: str):
    user = User(user_name=user_name, password=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, user_name: str, password: str):
    """校验用户名和密码，返回用户对象或None"""
    user = get_user_by_username(db, user_name)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def get_user_history(db: Session, user_id: int):
    return db.query(History).filter(History.user_id == user_id).all()