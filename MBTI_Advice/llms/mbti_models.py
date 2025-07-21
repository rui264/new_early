from config.settings import get_llm_config
from starlette.config import environ
from dotenv import load_dotenv
import os

from .custom_spark import CustomChatSpark
from utils import vector_db  # 导入向量数据库客户端

load_dotenv()
from .custom_qianwen import CustomQianWenChat  # 相对导入

def get_llm_for_mbti(mbti_type: str):
    """根据MBTI类型获取对应的LLM实例，支持多平台和多模型名"""
    config = get_llm_config(mbti_type)
    model_platform = config.get("model_platform") or config.get("platform") or config.get("model_name")
    # 兼容旧配置，优先用MBTI_MODEL_MAPPING
    from config.settings import settings
    model_platform = settings.MBTI_MODEL_MAPPING.get(mbti_type, "openai")
    model_name = config.get("model_name", "gpt-3.5-turbo")

    try:
        # OpenAI & DeepSeek（都用ChatOpenAI，区分base_url）
        if model_platform in ["openai", "deepseek"]:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=config["api_key"],
                base_url=config["base_url"],
                model_name=model_name,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 1024)
            )
        # 智谱清言
        elif model_platform == "zhipu":
            try:
                from langchain_zhipu import ChatZhipuAI
            except ImportError:
                raise ImportError("请安装 langchain_zhipu 以支持智谱清言")
            return ChatZhipuAI(
                api_key=config["api_key"],
                model_name=model_name,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 1024)
            )
        # 通义千问
        elif model_platform == "qwen":
            try:
                # 使用自定义客户端替代langchain_qianwen
                return CustomQianWenChat(
                    api_key=settings.QWEN_API_KEY,
                    model_name=config.get("model_name", "qwen-max"),
                    temperature=config.get("temperature", 0.7),
                    max_tokens=config.get("max_tokens", 1024),
                )
            except Exception as e:
                raise Exception(f"初始化通义千问模型失败: {str(e)}")
        elif model_platform == "spark":
            try:
                from .custom_spark import CustomChatSpark
                return CustomChatSpark(
                    app_id=settings.SPARK_APP_ID,  # 添加 app_id
                    api_key=settings.SPARK_API_KEY,
                    api_secret=settings.SPARK_API_SECRET,  # 添加 api_secret
                    model_name=config.get("model_name", "spark"),
                    temperature=config.get("temperature", 0.7),
                    max_tokens=config.get("max_tokens", 1024),
                )
            except Exception as e:
                raise Exception(f"初始化讯飞星火模型失败: {str(e)}")
        # 豆包
        elif model_platform == "doubao":
            try:
                from langchain_doubao import ChatDoubao
            except ImportError:
                raise ImportError("请安装 langchain_doubao 以支持豆包")
            from starlette.config import environ
            return ChatDoubao(
                api_key=config["api_key"],
                access_key_id=environ("DOUBAO_ACCESS_KEY_ID"),
                access_key_secret=environ("DOUBAO_ACCESS_KEY_SECRET"),
                base_url=config.get("base_url"),
                model_name=model_name,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 1024)
            )
    except Exception as e:
        print(f"模型 {model_platform} 初始化失败，尝试降级: {e}")
        # 降级到DeepSeek作为备用
        deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
        deepseek_base_url = os.environ.get("DEEPSEEK_BASE_URL")
        if deepseek_api_key and deepseek_base_url:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=deepseek_api_key,
                base_url=deepseek_base_url,
                model_name="deepseek-chat",
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 1024)
            )
        else:
            raise ValueError("DeepSeek的环境变量未正确设置，请检查DEEPSEEK_API_KEY和DEEPSEEK_BASE_URL")
    except Exception as e:
        print(f"发生未知错误: {e}")
        raise
def get_advice_with_context(mbti_type: str, question: str) -> str:
    """结合向量数据库和 LLM 生成建议"""
    # 1. 从向量数据库获取相关建议
    relevant_advice = vector_db.query_advice(mbti_type, question)
    context = "\n".join(relevant_advice) if relevant_advice else "无相关背景知识"

    # 2. 获取 LLM 实例
    llm = get_llm_for_mbti(mbti_type)

    # 3. 构造提示词
    prompt = f"""
    你是一位 {mbti_type} 人格特质的顾问。以下是相关背景知识：
    {context}

    用户的问题：{question}

    请结合上述背景知识，给出专业建议。
    """
    return llm.invoke(prompt)