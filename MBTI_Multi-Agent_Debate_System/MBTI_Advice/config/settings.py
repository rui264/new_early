# config/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()  # 加载环境变量

class AppSettings(BaseSettings):
    """应用程序配置类"""
    # API 密钥
    OPENAI_API_KEY: str = Field(None, validation_alias="OPENAI_API_KEY")
    DEEPSEEK_API_KEY: str = Field(..., validation_alias="DEEPSEEK_API_KEY")
    ZHIPU_API_KEY: str = Field(None, validation_alias="ZHIPU_API_KEY")
    QWEN_API_KEY: str = Field(None, validation_alias="QWEN_API_KEY")
    # SPARK_API_KEY: str = Field(None, validation_alias="SPARK_API_KEY")
    # SPARK_API_SECRET: str = Field(None, validation_alias="SPARK_API_SECRET")
    DOUBAO_API_KEY: str = Field(None, validation_alias="DOUBAO_API_KEY")
    DOUBAO_ACCESS_KEY_ID: str = Field(None, validation_alias="DOUBAO_ACCESS_KEY_ID")
    DOUBAO_ACCESS_KEY_SECRET: str = Field(None, validation_alias="DOUBAO_ACCESS_KEY_SECRET")
    SERPAPI_API_KEY: str = Field(..., validation_alias="SERPAPI_API_KEY")

    # API 基础 URL
    OPENAI_BASE_URL: str = Field("https://api.openai.com/v1", validation_alias="OPENAI_BASE_URL")
    DEEPSEEK_BASE_URL: str = Field("https://api.deepseek.com/v1", validation_alias="DEEPSEEK_BASE_URL")
    ZHIPU_BASE_URL: str = Field(None, validation_alias="ZHIPU_BASE_URL")
    # QWEN_BASE_URL: str = Field(None, validation_alias="QWEN_BASE_URL")
    SPARK_BASE_URL: str = Field(None, validation_alias="SPARK_BASE_URL")
    DOUBAO_BASE_URL: str = Field(None, validation_alias="DOUBAO_BASE_URL")

    SPARK_APP_ID: str = Field(..., validation_alias="SPARK_APP_ID")
    SPARK_API_KEY: str = Field(..., validation_alias="SPARK_API_KEY")
    SPARK_API_SECRET: str = Field(..., validation_alias="SPARK_API_SECRET")
    # 向量数据库路径
    VECTOR_DB_PATH: str = Field("mbti_vector_db", validation_alias="VECTOR_DB_PATH")

    # MBTI 到模型的映射
    MBTI_MODEL_MAPPING: Dict[str, str] = Field(
        {
            "INTJ": "openai",
            "INTP": "openai",
            "ENTJ": "openai",
            "ENTP": "openai",
            "INFJ": "deepseek",
            "INFP": "deepseek",
            "ENFJ": "qwen",
            "ENFP": "qwen",
            "ISTJ": "qwen",
            "ISFJ": "openai",
            "ESTJ": "openai",
            "ESFJ": "qwen",
            "ISTP": "deepseek",
            "ISFP": "deepseek",
            "ESTP": "deepseek",
            "ESFP": "deepseek",
        },
        validation_alias="MBTI_MODEL_MAPPING"
    )

    # MBTI 模型参数配置
    MBTI_MODEL_PARAMS: Dict[str, Dict[str, Any]] = Field(
        {
            "INTJ":  {"model_name": "gpt-3.5-turbo","temperature": 0.4, "max_tokens": 1000},
            "INTP":  {"model_name": "gpt-3.5-turbo","temperature": 0.7, "max_tokens": 1500},
            "ENTJ":  {"model_name": "gpt-3.5-turbo","temperature": 0.5, "max_tokens": 1000},
            "ENTP":  {"model_name": "gpt-3.5-turbo","temperature": 0.9, "max_tokens": 700},
            "INFJ":  {"model_name": "deepseek-chat","temperature": 0.8, "max_tokens": 1000},
            "INFP":  {"model_name": "deepseek-chat","temperature": 1.2, "max_tokens": 700},
            "ENFJ":  {"model_name": "qwen-max","temperature": 0.7, "max_tokens": 1000},
            "ENFP":  {"model_name": "qwen-max","temperature": 1.2, "max_tokens": 700},
            "ISTJ":  {"model_name": "qwen-max","temperature": 0.3, "max_tokens": 1000},
            "ISFJ":  {"model_name": "gpt-3.5-turbo","temperature": 0.6, "max_tokens": 1000},
            "ESTJ":  {"model_name": "gpt-3.5-turbo","temperature": 0.4, "max_tokens": 700},
            "ESFJ":  {"model_name": "qwen-max","temperature": 0.9, "max_tokens": 500},
            "ISTP":  {"model_name": "deepseek-chat","temperature": 0.5, "max_tokens": 700},
            "ISFP":  {"model_name": "deepseek-chat","temperature": 1.1, "max_tokens": 1000},
            "ESTP":  {"model_name": "deepseek-chat","temperature": 0.8, "max_tokens": 500},
            "ESFP":  {"model_name": "deepseek-chat","temperature": 1.3, "max_tokens": 400}
        },
        validation_alias="MBTI_MODEL_PARAMS"
    )

    # MBTI类型到风格描述的映射
    MBTI_TYPE_STYLE_MAP: Dict[str, str] = Field(
        {
            "INTJ": "理性、系统、善于规划，喜欢用全局视角分析问题",
            "ENFP": "热情、富有创意、善于激励他人，喜欢从多角度启发思考",
            "ISTJ": "务实、可靠、注重细节，喜欢用事实和经验来分析问题",
            "INFJ": "富有洞察力、理想主义、善于理解他人，喜欢用深刻的见解启发他人",
            "ENTJ": "果断、战略性强、善于领导，喜欢用高效的方法解决问题",
            "INFP": "理想主义、富有同情心、善于倾听，喜欢用温和的方式鼓励他人",
            "ESFP": "外向、乐观、善于交际，喜欢用实际行动带动氛围",
            "ISFJ": "细心、可靠、乐于助人，喜欢用温暖的方式支持他人",
            "ESTJ": "务实、组织能力强、注重效率，喜欢用直接的方法解决问题",
            "ESFJ": "关心他人、善于协调、注重和谐，喜欢用体贴的方式提出建议",
            "ISTP": "冷静、实际、善于动手，喜欢用简洁有效的方法分析问题",
            "ISFP": "温和、感性、注重体验，喜欢用真诚的方式表达建议",
            "ENTP": "机智、善于辩证、喜欢创新，喜欢用新颖的观点启发他人",
            "ESTP": "果断、现实、善于应变，喜欢用直接的方式解决问题",
            "INFJ": "富有洞察力、理想主义、善于理解他人，喜欢用深刻的见解启发他人",
            "ENFJ": "富有同理心、善于激励、注重团队，喜欢用鼓舞人心的方式提出建议",
        },
        validation_alias="MBTI_TYPE_STYLE_MAP"
    )

    # 通用MBTI提示词模板
    MBTI_PROMPT_TEMPLATE: str = Field(
        """
你是一位具有 {mbti_type} 人格特质的顾问。你的风格是{style_desc}。

请用 {mbti_type} 的思维方式，针对下述用户困惑，给出一段自然流畅、整体连贯的建议。建议应体现你的风格特点，不必分点分步，只需像一位专业顾问那样整体表达你的看法和建议。

用户的问题：{user_query}

请直接输出你的建议，字数控制在100~500范围内，全部使用中文回答。
""",
        validation_alias="MBTI_PROMPT_TEMPLATE"
    )
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",  # 可选：禁止额外字段
    )

# 单例配置实例
settings = AppSettings()

def get_llm_config(mbti_type: str) -> dict:
    platform = settings.MBTI_MODEL_MAPPING.get(mbti_type, "deepseek")
    base_url = getattr(settings, f"{platform.upper()}_BASE_URL", None) or os.environ.get(f"{platform.upper()}_BASE_URL")
    api_key = getattr(settings, f"{platform.upper()}_API_KEY", None) or os.environ.get(f"{platform.upper()}_API_KEY")

    # 合并默认参数和MBTI特定参数
    default_params = {"model_name": "deepseek-chat", "base_url": base_url, "api_key": api_key}
    mbti_params = settings.MBTI_MODEL_PARAMS.get(mbti_type, {})

    # 保证始终返回字典
    return {**default_params, **mbti_params}

def get_prompt_template(mbti_type: str) -> str:
    """获取特定MBTI类型的提示词模板（自动填充风格描述）"""
    style_desc = settings.MBTI_TYPE_STYLE_MAP.get(mbti_type, "理性、系统、善于规划")
    return settings.MBTI_PROMPT_TEMPLATE.format(mbti_type=mbti_type, style_desc=style_desc, user_query="{user_query}")