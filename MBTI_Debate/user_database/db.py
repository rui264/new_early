from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 替换为你的MySQL连接信息
DATABASE_URL =  "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
