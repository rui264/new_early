import requests
from typing import List, Optional, Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain.schema import ChatGeneration, ChatResult, HumanMessage, AIMessage
from langchain.callbacks.manager import CallbackManagerForLLMRun

class CustomQianWenChat(BaseChatModel):
    """直接调用通义千问API的自定义实现，不依赖langchain_qianwen库"""

    api_key: str
    model_name: str = "qwen-max"
    temperature: float = 0.7
    max_tokens: int = 1024
    api_url: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    @property
    def _llm_type(self) -> str:
        return "custom-qianwen"

    def _generate(
            self,
            messages: List[HumanMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 构建请求体
        request_data = {
            "model": self.model_name,
            "input": {
                "messages": [{"role": "user", "content": msg.content} for msg in messages]
            },
            "parameters": {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                **kwargs
            }
        }

        # 发送请求
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=request_data,
                timeout=60  # 设置超时时间
            )
            response.raise_for_status()  # 检查请求是否成功
        except requests.exceptions.RequestException as e:
            raise Exception(f"通义千问API调用失败: {str(e)}")

        # 解析响应
        result = response.json()

        # 检查API返回是否包含错误
        if "error" in result:
            raise Exception(f"通义千问API返回错误: {result['error']}")

        # 提取生成的文本
        text = result.get("output", {}).get("text", "")
        if not text:
            raise Exception("通义千问API返回内容为空")

        # 创建正确的 ChatMessage 对象
        message = AIMessage(content=text)  # 创建 AIMessage 对象
        generation = ChatGeneration(message=message)  # 传递 message 参数

        return ChatResult(generations=[generation])

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """返回标识此LLM的参数"""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }