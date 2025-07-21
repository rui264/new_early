from fastapi import FastAPI, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

import asyncio
import json
import os
from pathlib import Path

from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

# from user_database.db import SessionLocal, engine
# from user_database.crud import create_user, get_user_by_username, authenticate_user, get_user_history
# from user_database.models import Base

from constants import MBTI_TYPES
from debate_engine import DebateEngine
from debate_manager import DebateManager
from config.settings import settings
from vector_db import vector_db  # Optional, if needed in API

#建表
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MBTI思辩交互系统",
    description="展示基于可选 MBTI 人格设定的 AI 模型就特定议题进行辩论的全流程",
    version="1.0.0"
)

# 添加CORS中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#定义数据模型
#讨论
class DiscussRequest(BaseModel):
    user_name:str
    question:str

class DiscussResponse(BaseModel):
    answer:str
    user_name:str
#辩论
class DabateRequest(BaseModel):
    user_name:str
    proposition:str

class DabateRespnse(BaseModel):
    user_name:str

# 根路径
@app.get("/")
def read_root():
    return {"欢迎使用": "MBTI思辩交互系统", "文档": "/docs"}

#登录
# def get_db():#创建一个数据库会话
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
# @app.post("/register")
# def uesr_register(user_name: str, password: str, db: Session = Depends(get_db)):
#     if get_user_by_username(db, user_name):
#         raise HTTPException(status_code=400, detail="用户名已存在")
#     create_user(db, user_name, password)
#     return {"msg": "注册成功"}
#
# @app.post("/login")
# def uesr_login(user_name: str, password: str, db: Session = Depends(get_db)):
#     user = authenticate_user(db, user_name, password)
#     if not user:
#         raise HTTPException(status_code=400, detail="用户名或密码错误")
#     return {"msg": "登录成功", "user_id": user.id}

@app.get("/mbti_types")
def get_mbti_types():
    """
    获取所有可选的MBTI类型，供前端下拉选择
    """
    return {"mbti_types": list(MBTI_TYPES)}

history_records=[]
@app.post("/debate")
async def start_debate(request: dict):
    topic = request.get("topic")
    mbti_config = request.get("mbti_config")
    if not topic or not mbti_config:
        raise HTTPException(status_code=400, detail="缺少辩题或辩手配置")

    for mbti in mbti_config.values():
        if mbti not in MBTI_TYPES:
            raise HTTPException(status_code=400, detail=f"无效的MBTI类型: {mbti}")

    manager = DebateManager(topic)
    for speaker_id, mbti in mbti_config.items():
        manager.state.set_mbti(speaker_id, mbti)
    engine = DebateEngine(manager)

    async def debate_stream():
        history = engine.run_full_debate(free_debate_rounds=5)
        history_records.append({"topic": topic, "mbti_config": mbti_config, "history": history})
        for speech in history:
            yield json.dumps(speech, ensure_ascii=False) + "\n"
            await asyncio.sleep(0.1)


    return StreamingResponse(debate_stream(), media_type="application/json")

@app.get("/history")
def get_history():
    return JSONResponse(content=history_records)

