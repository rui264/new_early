from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

class MBTIVectorDB:
    def __init__(self, db_path: str = "mbti_vector_db", use_embeddings: bool = True):
        self.db_path = db_path
        self.use_embeddings = use_embeddings
        self.embeddings = None
        self.vectorstore = None

    def initialize_db(self, data_dir: str = None):
        """初始化或加载向量数据库"""
        if self.use_embeddings:
            # 使用DeepSeek Embeddings (如果有) 或保留OpenAI作为备选
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=os.environ.get("DEEPSEEK_API_KEY", "") or
                               os.environ.get("OPENAI_API_KEY", "")
            )

    def get_relevant_info(self, query: str, k: int = 5):
        """获取与查询相关的 MBTI 特质信息"""
        if not self.vectorstore:
            self.initialize_db()

        return self.vectorstore.similarity_search(query, k=k)


from langchain.docstore.document import Document


class MockVectorDB:
    """模拟向量数据库，用于测试环境"""

    # 预定义MBTI相关信息
    MBTI_INFO = {
        "INTJ职业倾向核心特质": [
            Document(
                page_content="INTJ职业倾向核心特质：\n"
                             "- 逻辑分析能力强，擅长解决复杂问题\n"
                             "- 具有战略思维，喜欢规划长远目标\n"
                             "- 独立性高，偏好自主决策的工作环境\n"
                             "- 适合技术、科研、工程、战略规划等领域",
                metadata={"source": "mock_mbti_db"}
            )
        ],
        "INTJ职业优势与核心需求": [
            Document(
                page_content="INTJ职业优势：\n"
                             "- 快速理解复杂系统和抽象概念\n"
                             "- 善于制定高效策略和解决方案\n"
                             "- 追求精益求精，注重长期价值\n\n"
                             "INTJ核心需求：\n"
                             "- 挑战性和智力刺激\n"
                             "- 自主性和控制权\n"
                             "- 明确的目标和清晰的反馈",
                metadata={"source": "mock_mbti_db"}
            )
        ],
        # 其他预定义信息...
    }

    def initialize_db(self, data_dir: str = None):
        print("使用模拟向量数据库，不执行实际操作")

    def get_relevant_info(self, query: str, k: int = 5):
        """返回预定义的MBTI信息"""
        # 简单匹配查询，返回预定义内容
        return self.MBTI_INFO.get(query, [
            Document(
                page_content=f"关于'{query}'的通用MBTI建议：\n"
                             "1. 了解自己的性格优势和劣势\n"
                             "2. 寻找能发挥你特长的环境\n"
                             "3. 注意发展可能存在的短板\n"
                             "4. 与不同性格类型的人合作时保持开放心态",
                metadata={"source": "mock_mbti_db"}
            )
        ])