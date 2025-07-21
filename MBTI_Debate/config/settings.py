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
    QWEN_BASE_URL: str = Field('https://dashscope.aliyuncs.com/api/v1', validation_alias='QWEN_BASE_URL')  # 提供默认 URL
    DOUBAO_BASE_URL: str = Field(None, validation_alias="DOUBAO_BASE_URL")

    # 向量数据库路径
    VECTOR_DB_PATH: str = Field("mbti_vector_db", validation_alias="VECTOR_DB_PATH")
    VECTOR_DB_HOST: str = Field('localhost', validation_alias='VECTOR_DB_HOST')  # 默认本地主机
    VECTOR_DB_PORT: int = Field(8000, validation_alias='VECTOR_DB_PORT')  # 默认 Chroma HTTP 端口

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

    SERPAPI_API_KEY: str = Field(None, validation_alias='SERPAPI_API_KEY')
    SPARK_API_KEY: str = Field(None, validation_alias='SPARK_API_KEY')
    SPARK_API_SECRET: str = Field(None, validation_alias='SPARK_API_SECRET')
    SPARK_BASE_URL: str = Field(None, validation_alias='SPARK_BASE_URL')
    SPARK_APP_ID: str = Field(None, validation_alias='SPARK_APP_ID')

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',  # 改为 ignore 以容忍额外 env 变量
    )
    VECTOR_DB_HOST: str = Field("localhost", validation_alias="VECTOR_DB_HOST")
    VECTOR_DB_PORT: int = Field(8000, validation_alias="VECTOR_DB_PORT")
    CHROMA_API_KEY: str = Field(None, validation_alias="CHROMA_API_KEY")  # 可选

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