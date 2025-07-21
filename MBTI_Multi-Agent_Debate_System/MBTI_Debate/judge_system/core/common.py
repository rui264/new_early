from dataclasses import dataclass
from typing import List, Dict
from pydantic import BaseModel, Field
from enum import Enum

class DebateStage(str, Enum):
    OPENING = "立论"
    CROSS_EXAM = "质询"
    FREE_DEBATE = "自由辩论"
    SUMMARY = "总结"

@dataclass
class Speech:
    debater: str
    stage: str
    content: str
    #timestamp: str

@dataclass
class DebaterInfo:
    name: str
    mbti_type: str

@dataclass
class DebateInfo:
    motion: str
    pro_debaters: List[DebaterInfo]
    con_debaters: List[DebaterInfo]
    speeches: List[Speech]

# 用于接收dify传来的单条发言
class DifySpeechInput(BaseModel):
    debater_name: str = Field(..., description="辩手姓名")#Pro/Con
    mbti_type: str = Field(..., description="MBTI人格类型")
    stage: DebateStage = Field(..., description="辩论阶段")
    content: str = Field(..., description="发言内容")
    speech_id: str = Field(..., description="发言唯一标识")

# 用于接收dify传来的完整辩论
class DifyDebateInput(BaseModel):
    motion: str
    pro_debaters: List[Dict[str, str]]
    con_debaters: List[Dict[str, str]]
    speeches: List[DifySpeechInput]

# 单个维度评分
class SingleScore(BaseModel):
    dimension: str
    score: float
    comment: str

# 单条发言的所有维度评分
class SpeechScoreResult(BaseModel):
    speech_id: str
    debater_name: str
    stage: DebateStage
    dimension_scores: List[SingleScore]
    total_score: float
    average_score: float

# 辩手最终得分
class DebaterFinalScore(BaseModel):
    debater_name: str
    mbti_type: str
    dimension_averages: Dict[str, float]
    weighted_total: float
    rank: int
    overall_comment: str

# 总评分报告
class DebateScoreReport(BaseModel):
    motion: str
    total_speeches: int
    debater_scores: List[DebaterFinalScore]
    dimension_statistics: Dict[str, Dict[str, float]]
    overall_statistics: Dict[str, float]

# 用于自由辩论阶段整体评分
class FreeDebateSummaryInput(BaseModel):
    debater_name: str
    mbti_type: str
    all_speeches: List[str]
    opponent_speeches: List[str] = []