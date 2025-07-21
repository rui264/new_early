from langchain.tools import BaseTool
from langchain.utilities import SerpAPIWrapper
from utils.vector_db import MBTIVectorDB
from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)


class SearchMBTIDBTool(BaseTool):
    """查询MBTI特质向量数据库的工具"""
    name = "SearchMBTIDB"
    description = "当需要查询MBTI相关特质、理论或建议时使用"

    vector_db: MBTIVectorDB

    def _run(
            self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """同步运行查询"""
        results = self.vector_db.get_relevant_info(query)
        return "\n\n".join([f"来源: {doc.metadata.get('source', 'MBTI知识库')}\n内容: {doc.page_content}"
                            for doc in results])

    async def _arun(
            self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """异步运行查询"""
        return self._run(query, run_manager)


class InternetSearchTool(BaseTool):
    """互联网搜索工具"""
    name = "SearchInternet"
    description = "当需要查询最新的外部信息或案例时使用"

    search_engine: SerpAPIWrapper

    def __init__(self, serpapi_key: str):
        super().__init__()
        self.search_engine = SerpAPIWrapper(serpapi_key=serpapi_key)

    def _run(
            self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """同步运行搜索"""
        return self.search_engine.run(query)

    async def _arun(
            self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """异步运行搜索"""
        return self._run(query, run_manager)


def get_all_tools(vector_db: MBTIVectorDB, serpapi_key: str) -> list:
    """获取所有可用工具"""
    return [
        SearchMBTIDBTool(vector_db=vector_db),
        InternetSearchTool(serpapi_key=serpapi_key)
    ]