from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum

class DebateStage(Enum):
    OPENING = "立论"
    CROSS_EXAM = "质询"
    FREE_DEBATE = "自由辩论"
    SUMMARY = "总结"

@dataclass
class DebateConfig:
    motion: str
    pro_debaters: List[str]
    con_debaters: List[str]
    mbti_map: Dict[str, str]
    stages: List[DebateStage] = field(default_factory=lambda: [
        DebateStage.OPENING, DebateStage.CROSS_EXAM, DebateStage.FREE_DEBATE, DebateStage.SUMMARY
    ])
    # 支持自定义维度和权重
    dimensions: List[str] = field(default_factory=lambda: [
        "逻辑性，表达准确性", "论点质量和论据充分性", "发言是否符合MBTI人格化", "反驳力度"
    ])
    weights = {
        "逻辑性，表达准确性": 0.4,
        "论点质量和论据充分性": 0.3,
        "发言是否符合MBTI人格化": 0.2,
        "反驳力度": 0.1
    }
    # 通用prompt模板
    prompt_template = """
你是一名专业的辩论评委，请对以下辩论发言进行评分。

辩题: {motion}
辩论阶段: {stage}
辩手: {debater} (MBTI类型: {mbti_type})
评分维度: {dimension}
发言内容:
{content}
请严格区分不同辩手在本维度的表现，进行严格排名，区分彼此之间的分数。请根据实际表现拉开分数，最高分和最低分至少相差1分。
如果评分维度为“发言是否符合MBTI人格化”，请判断该发言是否既体现了{mbti_type}的典型风格，又保持了理性。如果出现了与MBTI类型不符的极端情绪化或非理性行为，请在评语中指出并适当扣分。

另外，必须在评语中直接引用发言中的关键句子或短语，并结合评分维度对引用的发言部分进行具体评价，这部分必须占总篇幅的20%以上，避免空泛。评语必须言之有物，不能只说“表现不错”或“可以提升”。
请返回JSON格式的评分结果，包含score(0-10分，保留两位小数)和简短评语（包含对{content}的部分引用和评价）comment，每个维度的评语必须单独换行，格式如下:
```json
{{"score": 7.5, "comment": "观点明确但论证可以更深入，发言中的“xx"内容论证有力，有力证明了论点。}}

""" 