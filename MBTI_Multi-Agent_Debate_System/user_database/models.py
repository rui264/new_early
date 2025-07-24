from sqlalchemy import ForeignKey, Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(32), unique=True, index=True, nullable=False)
    password = Column(String(128), nullable=False)

class History(Base):
    __tablename__ = "history"
    r_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_name=Column(String(32), unique=True, index=True, nullable=False)
    records = Column(String(1024), nullable=False)

from datetime import datetime


class DebateHistory(Base):
    __tablename__ = "debate_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    user_name = Column(String(32), index=True, nullable=False)
    topic = Column(String(255))
    mbti_config = Column(JSON)
    history = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class AdviceHistory(Base):
    __tablename__ = "advice_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    user_name = Column(String(32), index=True, nullable=False)
    question = Column(Text)
    mbti_types = Column(JSON)
    responses = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)