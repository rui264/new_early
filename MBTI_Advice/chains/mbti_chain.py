from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import BaseLLM
from langchain.schema import BaseMemory
from typing import Dict, List, Any, Optional
from utils.mbti_prompts import get_prompt_for_mbti


class MBTIAdviceChain(LLMChain):
    """基于MBTI类型生成建议的自定义链"""
    mbti_type: str
    vector_db: Optional[Any] = None  # 向量数据库引用，用于检索相关信息

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_llm(
            cls,
            llm: BaseLLM,
            mbti_type: str,
            vector_db: Optional[Any] = None,
            memory: Optional[BaseMemory] = None,
            **kwargs
    ) -> "MBTIAdviceChain":
        """从LLM创建链实例"""
        # 获取MBTI特定的提示词模板
        prompt_template = PromptTemplate(
            input_variables=["user_query", "relevant_info", "chat_history"],
            template=get_prompt_for_mbti(mbti_type, "{user_query}")
        )

        return cls(
            llm=llm,
            prompt=prompt_template,
            mbti_type=mbti_type,
            vector_db=vector_db,
            memory=memory,
            **kwargs
        )

    def _get_relevant_info(self, query: str) -> str:
        """获取与查询相关的MBTI特质信息"""
        if not self.vector_db:
            return ""

        docs = self.vector_db.get_relevant_info(query)
        return "\n\n".join([doc.page_content for doc in docs])

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        """执行链"""
        user_query = inputs["user_query"]

        # 获取相关信息
        relevant_info = self._get_relevant_info(user_query)

        # 准备输入
        chain_inputs = {
            "user_query": user_query,
            "relevant_info": relevant_info,
            "chat_history": inputs.get("chat_history", "")
        }

        # 调用LLM生成建议
        return super()._call(chain_inputs)


def create_mbti_chain(
        mbti_type: str,
        llm: BaseLLM,
        vector_db: Optional[Any] = None,
        memory: Optional[BaseMemory] = None
) -> MBTIAdviceChain:
    """创建MBTI建议链的工厂函数"""
    return MBTIAdviceChain.from_llm(
        llm=llm,
        mbti_type=mbti_type,
        vector_db=vector_db,
        memory=memory
    )