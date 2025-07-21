import os
# 禁用代理设置以避免连接问题
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

from langchain.agents import AgentType, initialize_agent, Tool
from langchain.utilities import SerpAPIWrapper
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from ..llms.mbti_models import get_llm_for_mbti
from ..utils.mbti_prompts import get_prompt_for_mbti
from ..utils.vector_db import MBTIVectorDB, MockVectorDB
from ..config.network_config import NetworkConfig, SerpAPIConfig, DEFAULT_OFFLINE_MODE


class MBTIAdviceAgent:
    def __init__(self, mbti_type: str, use_vector_db: bool = False, offline_mode: bool = None):
        self.mbti_type = mbti_type
        # 如果没有指定离线模式，使用默认配置
        if offline_mode is None:
            offline_mode = DEFAULT_OFFLINE_MODE
        self.offline_mode = offline_mode
        
        # 确保代理设置正确
        NetworkConfig.disable_proxy()
        
        self.llm = get_llm_for_mbti(mbti_type)
        # 仅在需要时初始化向量数据库
        if use_vector_db:
            self.vector_db = MBTIVectorDB()
        else:
            self.vector_db = MockVectorDB()

        # 定义 Agent 工具
        self.tools = self._get_tools()

        # 初始化 Agent
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )

    def _get_tools(self):
        """定义 Agent 可用的工具"""
        tools = []

        # 添加MBTI数据库搜索工具（无论是否使用真实数据库都添加）
        tools.append(
            Tool(
                name="SearchMBTIDB",
                func=lambda query: self.vector_db.get_relevant_info(query),
                description="当需要查询MBTI相关特质、理论或建议时使用"
            )
        )

        # 如果不在离线模式，添加网络搜索工具
        if not self.offline_mode:
            # 添加网络搜索工具，带错误处理
            def safe_search_internet(query):
                try:
                    # 创建新的SerpAPIWrapper实例，避免代理问题
                    search = SerpAPIWrapper()
                    return search.run(query)
                except Exception as e:
                    return f"网络搜索暂时不可用，错误信息: {str(e)}。请基于MBTI理论和已有知识提供建议。"
            
            tools.append(
                Tool(
                    name="SearchInternet",
                    func=safe_search_internet,
                    description="当需要查询最新的外部信息或案例时使用"
                )
            )
        else:
            # 离线模式下的备用工具
            def offline_analysis(query):
                return "当前处于离线模式，基于MBTI理论和已有知识进行分析。"
            
            tools.append(
                Tool(
                    name="OfflineAnalysis",
                    func=offline_analysis,
                    description="离线模式下的分析工具，基于MBTI理论提供建议"
                )
            )
        
        return tools

    def generate_advice(self, user_query: str, conversation_history: str = ""):
        """生成MBTI风格的建议"""
        # 构建提示词，包含用户问题和对话历史
        full_prompt = get_prompt_for_mbti(self.mbti_type, user_query)

        if conversation_history:
            full_prompt = f"对话历史:\n{conversation_history}\n\n{full_prompt}"

        # 运行 Agent 生成建议
        return self.agent.run(full_prompt)