from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

import asyncio
import json

from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from user_database import SessionLocal, engine
from user_database.crud import create_user, get_user_by_username, authenticate_user
from user_database import Base

from MBTI_Debate.constants import MBTI_TYPES
from MBTI_Debate.core.debate_engine import DebateEngine
from MBTI_Debate.core.debate_manager import DebateManager

# 导入MBTI建议系统
from MBTI_Advice.advice_system import MBTIAdviceSystem

#建表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MBTI思辩交互系统",
    description="展示基于可选 MBTI 人格设定的 AI 模型就特定议题进行辩论和建议的全流程",
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

# 定义数据模型
class UserLoginRequest(BaseModel):
    user_name: str
    password: str

class UserRegisterRequest(BaseModel):
    user_name: str
    password: str

class UserResponse(BaseModel):
    msg: str
    user_id: int = None

# 建议相关模型
class AdviceRequest(BaseModel):
    user_id: str
    question: str
    mbti_types: list[str]

class AdviceResponse(BaseModel):
    user_id: str
    responses: dict[str, str]

# 辩论相关模型
class DebateRequest(BaseModel):
    topic: str
    mbti_config: dict[str, str]

class DebateResponse(BaseModel):
    topic: str
    mbti_config: dict[str, str]

# 历史记录模型
class HistoryRecord(BaseModel):
    topic: str
    mbti_config: dict[str, str]
    history: list[dict]

# 全局变量存储历史记录
history_records = []
advice_records = []

# 根路径
@app.get("/")
def read_root():
    return {"欢迎使用": "MBTI思辩交互系统", "文档": "/docs"}

# 数据库会话管理
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 用户认证相关API
@app.post("/register", response_model=UserResponse)
def user_register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    if get_user_by_username(db, request.user_name):
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = create_user(db, request.user_name, request.password)
    return UserResponse(msg="注册成功", user_id=user.id)

@app.post("/login", response_model=UserResponse)
def user_login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = authenticate_user(db, request.user_name, request.password)
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    return UserResponse(msg="登录成功", user_id=user.id)

@app.get("/mbti_types")
def get_mbti_types():
    """获取所有可选的MBTI类型，供前端下拉选择"""
    return {"mbti_types": list(MBTI_TYPES)}

@app.get("/test_api")
async def test_api():
    """测试API连接和余额"""
    try:
        from MBTI_Debate.core.llm_client import LLMClient
        client = LLMClient()
        test_result = await client.test_connection()
        return {"status": "success", "message": "API连接正常", "result": test_result}
    except Exception as e:
        return {"status": "error", "message": f"API连接失败: {str(e)}"}

# 建议功能API
@app.post("/advice", response_model=AdviceResponse)
async def get_advice(request: AdviceRequest):
    """获取MBTI建议"""
    try:
        # 验证
        for mbti in request.mbti_types:#命名问题吗
            if mbti not in MBTI_TYPES:
                raise HTTPException(status_code=400, detail=f"无效的MBTI类型: {mbti}")
        
        # 创建建议系统实例
        advice_system = MBTIAdviceSystem(use_vector_db=False, offline_mode=True)
        
        # 获取建议
        responses = advice_system.process_user_query(
            user_id=request.user_id,
            query=request.question,
            mbti_types=request.mbti_types
        )
        
        # 保存建议记录
        advice_records.append({
            "user_id": request.user_id,
            "question": request.question,
            "mbti_types": request.mbti_types,
            "responses": responses
        })
        
        return AdviceResponse(user_id=request.user_id, responses=responses)
        
    except Exception as e:
        logger.error(f"建议生成失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"建议生成失败: {str(e)}")

@app.post("/advice/followup")
async def get_followup_advice(request: dict):
    """获取追问建议"""
    try:
        user_id = request.get("user_id")
        followup_question = request.get("question")
        mbti_targets = request.get("mbti_targets", [])
        
        if not user_id or not followup_question:
            raise HTTPException(status_code=400, detail="缺少用户ID或问题")
        
        # 创建建议系统实例
        advice_system = MBTIAdviceSystem(use_vector_db=False, offline_mode=True)
        
        # 获取追问建议
        responses = advice_system.process_followup(
            user_id=user_id,
            query=followup_question,
            mbti_targets=mbti_targets
        )
        
        return {"user_id": user_id, "responses": responses}
        
    except Exception as e:
        logger.error(f"追问建议生成失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"追问建议生成失败: {str(e)}")

# 辩论功能API
@app.post("/debate")
async def start_debate(request: dict):
    topic = request.get("topic")
    mbti_config = request.get("mbti_config")
    if not topic or not mbti_config:
        raise HTTPException(status_code=400, detail="缺少辩题或辩手配置")

    if not DebateManager.is_valid_debate_topic(topic):
        raise HTTPException(status_code=400, detail="输入内容不是辩题")
    
    for mbti in mbti_config.values():
        if mbti not in MBTI_TYPES:
            raise HTTPException(status_code=400, detail=f"无效的MBTI类型: {mbti}")

    manager = DebateManager(topic)
    for speaker_id, mbti in mbti_config.items():
        manager.state.set_mbti(speaker_id, mbti)
    engine = DebateEngine(manager)

    async def debate_stream():
        try:
            history = []
            for speech in engine.run_full_debate(free_debate_rounds=5):
                history.append(speech)
                
                # 发送发言开始信号
                yield json.dumps({
                    "type": "speech_start",
                    "agent_id": speech["agent_id"],
                    "stage": speech["stage"],
                    "round": speech["round"]
                }, ensure_ascii=False) + "\n"
                
                # 发送发言内容（逐字符流式输出）
                content = speech["content"]
                for char in content:
                    yield json.dumps({
                        "type": "speech_char",
                        "content": char
                    }, ensure_ascii=False) + "\n"
                    await asyncio.sleep(0.01)  # 控制字符输出速度
                
                # 发送发言完成信号
                yield json.dumps({
                    "type": "speech_complete",
                    "content": content,
                    "analysis": speech.get("analysis", [])
                }, ensure_ascii=False) + "\n"
                
                await asyncio.sleep(0.1)  # 发言间隔
            
            # 辩论完成后保存历史记录
            history_records.append({"topic": topic, "mbti_config": mbti_config, "history": history})
            
            # 发送完成信号
            yield json.dumps({
                "type": "complete",
                "message": "辩论完成"
            }, ensure_ascii=False) + "\n"
            
        except Exception as e:
            logger.error(f"辩论生成失败: {e}", exc_info=True)
            yield json.dumps({"type": "error", "error": f"生成失败: {str(e)}"}, ensure_ascii=False) + "\n"

    return StreamingResponse(debate_stream(), media_type="application/json")

# 历史记录API
@app.get("/history/debate")
def get_debate_history():
    """获取辩论历史记录"""
    return JSONResponse(content=history_records)

@app.get("/history/advice")
def get_advice_history():
    """获取建议历史记录"""
    return JSONResponse(content=advice_records)

@app.get("/history")
def get_all_history():
    """获取所有历史记录"""
    return JSONResponse(content={
        "debate_history": history_records,
        "advice_history": advice_records
    })

# 评分系统
