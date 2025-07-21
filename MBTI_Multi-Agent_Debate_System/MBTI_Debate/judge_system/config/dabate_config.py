from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum

class DebateStage(Enum):
    OPENING = "立论"
    CROSS_EXAM = "质询"
    FREE_SPEECH = "自由发言"
    SUMMARY = "总结"

@dataclass
class DebateConfig:
    motion: str
    pro_debaters: List[str]
    con_debaters: List[str]
    mbti_map: Dict[str, str]  # 例如 {"pro1": "INTJ", ...}
    stages: List[DebateStage] = field(default_factory=lambda: [
        DebateStage.OPENING, DebateStage.CROSS_EXAM, DebateStage.FREE_SPEECH, DebateStage.SUMMARY
    ])
    dimensions: List[str] = field(default_factory=lambda: [
        "逻辑性","论据质量","MBTI人格一致性","反驳力度"
    ])
    weights = {
        "逻辑性": 0.3,
        "论据质量": 0.3,
        "MBTI人格一致性": 0.2,
        "反驳力度": 0.2
    }

    prompt_template_1 ='''
    作为辩论评委，请从{dimension}维度对以下发言进行评分（1-10分）：
    辩论阶段：{stage}
    辩手：{debater}
    MBTI人格类型：{mbti_type}
    发言内容：{content}
    请分析发言的逻辑结构、推理过程、论证链条的完整性。
    评分标准：
    - 1-3分：逻辑混乱，论证不清晰
    - 4-6分：逻辑基本清晰，论证一般
    - 7-8分：逻辑清晰，论证有力
    - 9-10分：逻辑严密，论证充分
    
    请直接返回JSON格式的评分(保留一位小数)和简短理由，例如：
    {{"score": 8.2, "reason": "论点逻辑严密，但缺少数据支撑"}}
    '''
    # 模板2 - 论据质量评分
    prompt_template_2 = """
    作为辩论评委，请从{dimension}维度对以下发言进行评分（1-10分）：

    辩论阶段：{stage}
    辩手：{debater}
    MBTI人格类型：{mbti_type}
    发言内容：{content}

    请分析论据的相关性、可靠性、充分性和说服力。
    评分标准：
    - 1-3分：论据不相关或不可靠
    - 4-6分：论据基本相关，可靠性一般
    - 7-8分：论据相关且可靠
    - 9-10分：论据充分且极具说服力
    请直接返回JSON格式的评分(保留一位小数)和简短理由，例如：
    {{"score": 8.2, "reason": "论点逻辑严密，但缺少数据支撑"}}

    """

    # 模板3 - MBTI人格一致性评分
    prompt_template_3 = """
    作为辩论评委，请从{dimension}维度对以下发言进行评分（1-10分）：

    辩论阶段：{stage}
    辩手：{debater}
    MBTI人格类型：{mbti_type}
    发言内容：{content}

    请分析发言风格、思维方式、表达特点是否符合该MBTI人格类型{mbti_type}的典型特征。
    评分标准：
    - 1-3分：与MBTI特征不符
    - 4-6分：部分符合MBTI特征
    - 7-8分：较好地体现了MBTI特征
    - 9-10分：完美体现了MBTI特征
    请直接返回JSON格式的评分(保留一位小数)和简短理由，例如：
    {{"score": 8.2, "reason": "论点逻辑严密，但缺少数据支撑"}}
    """

    # 模板4 - 反驳力度评分
    prompt_template_4 = """
    作为辩论评委，请从{dimension}维度对以下发言进行评分（1-10分）：

    辩论阶段：{stage}
    辩手：{debater}
    MBTI人格类型：{mbti_type}
    发言内容：{content}

    请分析反驳的针对性、力度、有效性和创新性。
    评分标准：
    - 1-3分：反驳无力或偏离重点
    - 4-6分：反驳基本有效
    - 7-8分：反驳有力且有效
    - 9-10分：反驳精准且极具杀伤力
    请直接返回JSON格式的评分(保留一位小数)和简短理由，例如：
    {{"score": 8.2, "reason": "论点逻辑严密，但缺少数据支撑"}}
    """