# 用户操作函数
from sqlalchemy.orm import Session
from .models import User, DebateHistory, AdviceHistory
from .security import get_password_hash, verify_password
from datetime import datetime

def get_user_by_username(db: Session, user_name: str):
    return db.query(User).filter(User.user_name == user_name).first()

def create_user(db: Session, user_name: str, password: str):
    user = User(user_name=user_name, password=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, user_name: str, password: str):
    user = get_user_by_username(db, user_name)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def create_debate_history_by_name(db: Session, user_name: str, topic: str, mbti_config: dict, history: list):
    user = get_user_by_username(db, user_name)
    if not user:
        return None
    db_history = DebateHistory(
        user_id=user.id,
        user_name=user_name,
        topic=topic,
        mbti_config=mbti_config,
        history=history,
        created_at=datetime.utcnow()
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_user_debate_history_by_name(db: Session, user_name: str, limit: int = 10):
    return db.query(DebateHistory).filter(
        DebateHistory.user_name == user_name
    ).order_by(
        DebateHistory.created_at.desc()
    ).limit(limit).all()

def create_advice_history_by_name(db: Session, user_name: str, question: str, mbti_types: list, responses: dict):
    user = get_user_by_username(db, user_name)
    if not user:
        return None
    db_history = AdviceHistory(
        user_id=user.id,
        user_name=user_name,
        question=question,
        mbti_types=mbti_types,
        responses=responses,
        created_at=datetime.utcnow()
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_user_advice_history_by_name(db: Session, user_name: str, limit: int = 10):
    return db.query(AdviceHistory).filter(
        AdviceHistory.user_name == user_name
    ).order_by(
        AdviceHistory.created_at.desc()
    ).limit(limit).all()