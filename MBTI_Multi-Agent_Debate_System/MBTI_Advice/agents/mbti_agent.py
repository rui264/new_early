from langchain.agents import AgentType, initialize_agent, Tool
from langchain.utilities import SerpAPIWrapper
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from ..llms.mbti_models import get_llm_for_mbti
from ..utils.mbti_prompts import get_prompt_for_mbti
from ..utils.vector_db import MBTIVectorDB, MockVectorDB


class MBTIAdviceAgent:
    def __init__(self, mbti_type: str,use_vector_db: bool = False):
        self.mbti_type = mbti_type
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

        # # 添加其他工具
        # tools.append(
        #     Tool(
        #         name="SearchInternet",
        #         func=SerpAPIWrapper().run,
        #         description="当需要查询最新的外部信息或案例时使用"
        #     )
        # )
        return tools

    def generate_advice(self, user_query: str, conversation_history: str = ""):
        """生成MBTI风格的建议"""
        # 构建提示词，包含用户问题和对话历史
        full_prompt = get_prompt_for_mbti(self.mbti_type, user_query)

        if conversation_history:
            full_prompt = f"对话历史:\n{conversation_history}\n\n{full_prompt}"

        # 运行 Agent 生成建议
        return self.agent.run(full_prompt)