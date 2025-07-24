import json
import os
from typing import List, Dict
from ..core.common import Speech, DebateInfo
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv
import re

load_dotenv()

class JudgeAgent:
    def __init__(self, name: str, dimensions: List[str], prompt_template: str):
        self.name = name
        self.dimensions = dimensions  # 只负责一个维度
        self.prompt_template = prompt_template
        # 直接用langchain的ChatOpenAI对接deepseek
        self.llm = ChatOpenAI(
            model_name="deepseek-chat",
            temperature=0.3,
            base_url=os.environ["DEEPSEEK_BASE_URL"],
            api_key=os.environ["DEEPSEEK_API_KEY"],
            max_tokens=1000
        )

    def _extract_json(self, text: str) -> str:
        # 先去除 markdown 代码块标记
        text = re.sub(r"^```json\\s*|^```\\s*|```$", "", text.strip(), flags=re.MULTILINE)
        text = text.strip()
        # 尝试直接解析
        try:
            json.loads(text)
            return text
        except Exception:
            pass
        # 尝试用正则提取第一个合法JSON对象
        match = re.search(r'\{[\s\S]*?\}', text)
        if match:
            candidate = match.group(0)
            try:
                json.loads(candidate)
                return candidate
            except Exception:
                pass
        # 兜底返回原始内容
        return text

    async def score_speech(self, speech: Speech, debate_info: DebateInfo) -> Dict[str, float]:
        scores = {}
        for dim in self.dimensions:
            prompt = self.prompt_template.format(
                motion=getattr(debate_info, 'motion', ''),  
                stage=speech.stage,
                debater=speech.debater,
                mbti_type=getattr(speech, 'mbti_type', '未知'),
                dimension=dim,
                content=speech.content
            )
            try:
                text = await self.call_deepseek_llm(prompt)
                clean_text = self._extract_json(text)
                try:
                    score_json = json.loads(clean_text)
                    if not isinstance(score_json, dict):
                        raise ValueError("Response is not a JSON object")
                    scores[dim] = float(score_json.get("score", 5.0))
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"JSON解析失败: {e}, 原始响应: {text}")
                    scores[dim] = 5.0
            except Exception as e:
                print(f"API调用失败: {e}")
                scores[dim] = 5.0
        return scores

    async def call_deepseek_llm(self, prompt: str) -> str:
        import asyncio
        loop = asyncio.get_event_loop()
        # 支持同步和异步llm.invoke
        if hasattr(self.llm, 'ainvoke'):
            result = await self.llm.ainvoke(prompt)
        else:
            result = await loop.run_in_executor(None, lambda: self.llm.invoke(prompt))
        if hasattr(result, 'content'):
            return result.content
        return str(result)