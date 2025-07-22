# llms/custom_spark.py

import requests
from typing import List, Optional, Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain.schema import ChatGeneration, ChatResult, HumanMessage, AIMessage
from langchain.callbacks.manager import CallbackManagerForLLMRun


class CustomChatSpark(BaseChatModel):
    """自定义讯飞星火大模型客户端"""

    app_id: str
    api_key: str
    api_secret: str
    model_name: str = "spark"
    temperature: float = 0.7
    max_tokens: int = 1024

    @property
    def _llm_type(self) -> str:
        return "custom-spark"

    def _generate(
            self,
            messages: List[HumanMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        # 构建请求体
        user_messages = [msg.content for msg in messages]
        prompt = "\n".join(user_messages)

        # 这里需要根据讯飞星火API的实际格式构建请求
        # 以下是示例代码，需要根据实际API文档调整
        headers = {
            "Content-Type": "application/json",
            # 添加认证头
        }

        request_data = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs
        }

        # 发送请求
        try:
            response = requests.post(
                "https://spark-api.xfyun.cn/v2.1/chat",  # 修改为正确的API地址
                headers=headers,
                json=request_data,
                timeout=60
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"讯飞星火API调用失败: {str(e)}")

        # 解析响应
        result = response.json()

        # 提取生成的文本（根据实际API响应格式调整）
        text = result.get("data", {}).get("result", "")
        if not text:
            raise Exception("讯飞星火API返回内容为空")

        message = AIMessage(content=text)
        generation = ChatGeneration(message=message)

        return ChatResult(generations=[generation])

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }