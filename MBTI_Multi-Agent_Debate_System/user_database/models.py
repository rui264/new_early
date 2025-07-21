from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

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
