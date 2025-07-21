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
    DOUBAO_API_KEY: str = Field(None, validation_alias="DOUBAO_API_KEY")
    DOUBAO_ACCESS_KEY_ID: str = Field(None, validation_alias="DOUBAO_ACCESS_KEY_ID")
    DOUBAO_ACCESS_KEY_SECRET: str = Field(None, validation_alias="DOUBAO_ACCESS_KEY_SECRET")

    # API 基础 URL
    OPENAI_BASE_URL: str = Field("https://api.openai.com/v1", validation_alias="OPENAI_BASE_URL")
    DEEPSEEK_BASE_URL: str = Field("https://api.deepseek.com/v1", validation_alias="DEEPSEEK_BASE_URL")
    ZHIPU_BASE_URL: str = Field(None, validation_alias="ZHIPU_BASE_URL")
    QWEN_BASE_URL: str = Field('https://dashscope.aliyuncs.com/api/v1', validation_alias='QWEN_BASE_URL')
    DOUBAO_BASE_URL: str = Field(None, validation_alias="DOUBAO_BASE_URL")

    # 向量数据库配置（确保只定义一次！）
    VECTOR_DB_HOST: str = Field('localhost', validation_alias='VECTOR_DB_HOST')
    VECTOR_DB_PORT: int = Field(8000, validation_alias='VECTOR_DB_PORT')
    CHROMA_API_KEY: str = Field(None, validation_alias="CHROMA_API_KEY")  # 可选认证
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
            "INTJ": {"model_name": "gpt-3.5-turbo", "temperature": 0.4, "max_tokens": 1000},
            "INTP": {"model_name": "gpt-3.5-turbo", "temperature": 0.7, "max_tokens": 1500},
            "ENTJ": {"model_name": "gpt-3.5-turbo", "temperature": 0.5, "max_tokens": 1000},
            "ENTP": {"model_name": "gpt-3.5-turbo", "temperature": 0.9, "max_tokens": 700},
            "INFJ": {"model_name": "deepseek-chat", "temperature": 0.8, "max_tokens": 1000},
            "INFP": {"model_name": "deepseek-chat", "temperature": 1.2, "max_tokens": 700},
            "ENFJ": {"model_name": "qwen-max", "temperature": 0.7, "max_tokens": 1000},
            "ENFP": {"model_name": "qwen-max", "temperature": 1.2, "max_tokens": 700},
            "ISTJ": {"model_name": "qwen-max", "temperature": 0.3, "max_tokens": 1000},
            "ISFJ": {"model_name": "gpt-3.5-turbo", "temperature": 0.6, "max_tokens": 1000},
            "ESTJ": {"model_name": "gpt-3.5-turbo", "temperature": 0.4, "max_tokens": 700},
            "ESFJ": {"model_name": "qwen-max", "temperature": 0.9, "max_tokens": 500},
            "ISTP": {"model_name": "deepseek-chat", "temperature": 0.5, "max_tokens": 700},
            "ISFP": {"model_name": "deepseek-chat", "temperature": 1.1, "max_tokens": 1000},
            "ESTP": {"model_name": "deepseek-chat", "temperature": 0.8, "max_tokens": 500},
            "ESFP": {"model_name": "deepseek-chat", "temperature": 1.3, "max_tokens": 400}
        },
        validation_alias="MBTI_MODEL_PARAMS"
    )

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'  # 忽略额外字段
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
    """根据 MBTI 类型返回对应的提示词模板"""
    templates = {
        "INTJ": "你是一个理性且战略性的 INTJ，请分析以下问题：{question}",
        "INTP": "你是一个逻辑严谨的 INTP，请从多角度拆解问题：{question}",
        "ENTJ": "你是一个目标明确的 ENTJ，请提出高效解决方案：{question}",
        "ENTP": "你是一个创意无限的 ENTP，请提供突破性思路：{question}",
        "INFJ": "你是一个富有洞察力的 INFJ，请揭示问题的深层意义：{question}",
        "INFP": "你是一个理想主义的 INFP，请从情感角度回答：{question}",
        "ENFJ": "你是一个充满感染力的 ENFJ，请激励他人参与讨论：{question}",
        "ENFP": "你是一个热情洋溢的 ENFP，请用新颖视角解读问题：{question}",
        "ISTJ": "你是一个务实可靠的 ISTJ，请给出具体执行步骤：{question}",
        "ISFJ": "你是一个细致周到的 ISFJ，请考虑实际需求和细节：{question}",
        "ESTJ": "你是一个高效组织的 ESTJ，请制定清晰的行动计划：{question}",
        "ESFJ": "你是一个关怀他人的 ESFJ，请平衡各方利益：{question}",
        "ISTP": "你是一个冷静分析的 ISTP，请用技术手段解决问题：{question}",
        "ISFP": "你是一个艺术敏感的 ISFP，请用美感表达观点：{question}",
        "ESTP": "你是一个灵活应变的 ESTP，请快速提出实用方案：{question}",
        "ESFP": "你是一个活力四射的 ESFP，请用生动方式阐述：{question}"
    }
    return templates.get(mbti_type, "请用中文回答以下问题：{question}")