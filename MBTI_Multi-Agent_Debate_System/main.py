from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

import asyncio
import json

from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from MBTI_Debate.judge_system.agents.judge_agent import JudgeAgent
from MBTI_Debate.judge_system.config.dabate_config import DebateConfig
from MBTI_Debate.judge_system.core.common import DifySpeechInput
from MBTI_Debate.judge_system.scoring.dimension import ScoreAggregator
from MBTI_Debate.judge_system.scoring.evaluator import Evaluator
from user_database import SessionLocal, engine
from user_database.crud import create_user, get_user_by_username, authenticate_user, \
    create_debate_history_by_name, get_user_debate_history_by_name, \
    create_advice_history_by_name, get_user_advice_history_by_name
from user_database import Base

from MBTI_Debate.constants import MBTI_TYPES
from MBTI_Debate.core.debate_engine import DebateEngine
from MBTI_Debate.core.debate_manager import DebateManager

from MBTI_Advice.agents.mbti_agent import MBTIAdviceAgent
from MBTI_Advice.memory.conversation_memory import MBTIConversationMemory
from user_database.models import AdviceHistory, DebateHistory


# 建表
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
    user_name: str
    question: str
    mbti_types: list[str]


class AdviceResponse(BaseModel):
    user_name: str
    responses: dict[str, str]


# 辩论相关模型
class DebateRequest(BaseModel):
    user_name: str
    topic: str
    mbti_config: dict[str, str]


class DebateResponse(BaseModel):
    user_name: str
    topic: str
    mbti_config: dict[str, str]


# 历史记录模型
class HistoryRecord(BaseModel):
    topic: str
    mbti_config: dict[str, str]
    history: list[dict]


# 全局变量存储历史记录:存到内存中
#history_records = []
#advice_records = []


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
async def get_advice(request: AdviceRequest,db: Session = Depends(get_db)):
    """获取MBTI建议（支持多选mbti类型）"""
    try:
        for mbti in request.mbti_types:
            if mbti not in MBTI_TYPES:
                raise HTTPException(status_code=400, detail=f"无效的MBTI类型: {mbti}")
        # 初始化对话记忆
        memory = MBTIConversationMemory()
        responses = {}
        for mbti in request.mbti_types:
            agent = MBTIAdviceAgent(mbti)
            advice = agent.generate_advice(request.question, memory.get_history(request.user_name))
            responses[mbti] = advice
            memory.add_message(request.user_name, mbti, advice, is_user=False)
        create_advice_history_by_name(
            db=db,
            user_name=request.user_name,
            question=request.question,
            mbti_types=request.mbti_types,
            responses=responses
        )
        return AdviceResponse(user_name=request.user_name, responses=responses)
    except Exception as e:
        logger.error(f"建议生成失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"建议生成失败: {str(e)}")


@app.post("/advice/followup")
async def get_followup_advice(request: dict):
    """获取追问建议（支持@MBTI类型，仅被@到的类型回复）"""
    try:
        user_name = request.get("user_name")
        followup_question = request.get("question")
        mbti_targets = request.get("mbti_targets", [])
        if not user_name or not followup_question:
            raise HTTPException(status_code=400, detail="缺少用户名或问题")
        # 解析@信息
        at_mbti = []
        question = followup_question
        if followup_question.startswith("@"):  # 例如 @INTJ,ENFP 你怎么看？
            parts = followup_question.split(" ", 1)
            at_part = parts[0][1:]  # 去掉@，如 INTJ,ENFP
            at_mbti = [t.strip() for t in at_part.split(",") if t.strip() in MBTI_TYPES]
            question = parts[1] if len(parts) > 1 else ""
        # 如果mbti_targets未指定，则用@到的类型，否则用传入的
        targets = mbti_targets if mbti_targets else at_mbti
        if not targets:
            raise HTTPException(status_code=400, detail="未指定需要回复的MBTI类型")
        # 初始化对话记忆
        memory = MBTIConversationMemory()
        responses = {}
        for mbti in targets:
            agent = MBTIAdviceAgent(mbti)
            advice = agent.generate_advice(question, memory.get_history(user_name))
            responses[mbti] = advice
            memory.add_message(user_name, mbti, advice, is_user=False)
        return {"user_name": user_name, "responses": responses}
    except Exception as e:
        logger.error(f"追问建议生成失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"追问建议生成失败: {str(e)}")


# 辩论功能API
@app.post("/debate")
async def start_debate(request: dict,db: Session = Depends(get_db)):
    topic = request.get("topic")
    mbti_config = request.get("mbti_config")
    user_name = request.get("user_name")
    if not topic or not mbti_config or not user_name:
        raise HTTPException(status_code=400, detail="缺少辩题、辩手配置或用户名")

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
            #history_records.append({"topic": topic, "mbti_config": mbti_config, "history": history})

            create_debate_history_by_name(
                db=db,
                user_name=user_name,
                topic=topic,
                mbti_config=mbti_config,
                history=history
            )
            # 发送完成信号
            yield json.dumps({
                "type": "complete",
                "message": "辩论完成"
            }, ensure_ascii=False) + "\n"

        except Exception as e:
            logger.error(f"辩论生成失败: {e}", exc_info=True)
            yield json.dumps({"type": "error", "error": f"生成失败: {str(e)}"}, ensure_ascii=False) + "\n"

    return StreamingResponse(debate_stream(), media_type="application/json")


# 修改历史记录获取接口
@app.get("/history/debate")
def get_debate_history(user_name: str, db: Session = Depends(get_db)):
    """获取用户辩论历史记录"""
    records = get_user_debate_history_by_name(db, user_name)
    return [{
        "id": record.id,
        "user_name": record.user_name,
        "topic": record.topic,
        "mbti_config": record.mbti_config,
        "history": record.history,
        "created_at": record.created_at.isoformat()
    } for record in records]

@app.get("/history/debate/{record_id}")
def get_debate_history_detail(record_id: int, db: Session = Depends(get_db)):
    """获取辩论历史详情"""
    record = db.query(DebateHistory).filter(DebateHistory.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {
        "id": record.id,
        "topic": record.topic,
        "mbti_config": record.mbti_config,
        "history": record.history,
        "created_at": record.created_at.isoformat()
    }

@app.get("/history/advice")
def get_advice_history(user_name: str, db: Session = Depends(get_db)):
    """获取用户建议历史记录"""
    records = get_user_advice_history_by_name(db, user_name)
    return [{
        "id": record.id,
        "user_name": record.user_name,
        "question": record.question,
        "mbti_types": record.mbti_types,
        "responses": record.responses,
        "created_at": record.created_at.isoformat()
    } for record in records]

@app.get("/history/advice/{record_id}")
def get_advice_history_detail(record_id: int, db: Session = Depends(get_db)):
    """获取建议历史详情"""
    record = db.query(AdviceHistory).filter(AdviceHistory.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {
        "id": record.id,
        "question": record.question,
        "mbti_types": record.mbti_types,
        "responses": record.responses,
        "created_at": record.created_at.isoformat()
    }

@app.get("/history")
def get_all_history(user_name: str, db: Session = Depends(get_db)):
    debate_history = get_user_debate_history_by_name(db, user_name)
    advice_history = get_user_advice_history_by_name(db, user_name)
    return {
        "debate_history": [{
            "id": record.id,
            "user_name": record.user_name,
            "topic": record.topic,
            "mbti_config": record.mbti_config,
            "history": record.history,
            "created_at": record.created_at.isoformat()
        } for record in debate_history],
        "advice_history": [{
            "id": record.id,
            "user_name": record.user_name,
            "question": record.question,
            "mbti_types": record.mbti_types,
            "responses": record.responses,
            "created_at": record.created_at.isoformat()
        } for record in advice_history]
    }

@app.get("/debate_score/view")
async def view_debate_score(user_name: str, topic: str, db: Session = Depends(get_db)):
    record = db.query(DebateHistory).filter(DebateHistory.user_name==user_name, DebateHistory.topic==topic).order_by(DebateHistory.id.desc()).first()
    if not record:
        raise HTTPException(status_code=404, detail="未找到对应辩论历史")
    mbti_config = record.mbti_config
    # 统一stage字段映射
    stage_map = {
        "立论": "OPENING",
        "攻辩": "CROSS_EXAM",
        "自由辩论": "FREE_DEBATE",
        "总结": "SUMMARY",
        "总结陈词": "SUMMARY"
    }
    speech_inputs = []
    for s in record.history:
        # 判断是否为标准格式
        if all(k in s for k in ("debater_name", "mbti_type", "stage", "content", "speech_id")):
            s["debater_name"] = s["debater_name"].strip().lower()
            s["stage"] = stage_map.get(s["stage"], s["stage"])
            speech_inputs.append(DifySpeechInput(**s))
        else:
            debater_name = (s.get("debater_name") or s.get("agent_id") or "").strip().lower()
            mbti_type = s.get("mbti_type") or mbti_config.get(debater_name, "未知")
            stage = s.get("stage")
            stage = stage_map.get(stage, stage)
            content = s.get("content")
            speech_id = s.get("speech_id") or f"{debater_name}_{s.get('round', 1)}"
            speech_inputs.append(DifySpeechInput(
                debater_name=debater_name,
                mbti_type=mbti_type,
                stage=stage,
                content=content,
                speech_id=speech_id
            ))
    #print("所有speech_inputs的debater_name和mbti_type：", [(s.debater_name, s.mbti_type) for s in speech_inputs], flush=True)
    # 评分遍历所有实际出现的stage
    all_stages = set(s.stage for s in speech_inputs)
    config = DebateConfig(
        motion=topic,
        pro_debaters=[k for k in mbti_config if k.startswith("pro")],
        con_debaters=[k for k in mbti_config if k.startswith("opp")],
        mbti_map=mbti_config
    )
    judge_agents = [
        JudgeAgent(f"Judge-{dim}", [dim], prompt_template=config.prompt_template) for dim in config.dimensions
    ]
    evaluator = Evaluator(judge_agents, config.dimensions, config.weights)
    # 评分遍历所有实际出现的stage
    async def evaluate_all_stages(speeches, stages):
        results = []
        tasks = [evaluator.evaluate_stage(speeches, stage) for stage in stages]
        stage_results = await asyncio.gather(*tasks)
        for r in stage_results:
            results.extend(r)
        # 自由辩论特殊处理
        if "FREE_DEBATE" in stages:
            free_results = await evaluator.evaluate_free_debate(speeches)
            results.extend(free_results)
        return results
    speech_scores = await evaluate_all_stages(speech_inputs, all_stages)
    aggregator = ScoreAggregator(config.dimensions, config.weights)
    final_scores = await aggregator.aggregate_speech_scores_async(speech_scores, judge_agents[0])
    return {"scores": [
        {
            "debater_name": s.debater_name,
            "mbti_type": s.mbti_type,
            "total_score": s.total_score,
            "overall_comment": s.overall_comment,
            "rank": s.rank
        } for s in final_scores.values()
    ]}