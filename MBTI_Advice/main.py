from agents.mbti_agent import MBTIAdviceAgent
from memory.conversation_memory import MBTIConversationMemory
import os
from dotenv import load_dotenv

load_dotenv()  # 加载环境变量

"""

"""

class MBTIAdviceSystem:
    def __init__(self, use_vector_db: bool = False):
        self.use_vector_db = use_vector_db
        self.memory = MBTIConversationMemory()
        self.active_agents = {}  # MBTI 类型到 Agent 的映射

    # 首次提问函数
    def process_user_query(self, user_id: str, query: str, mbti_types: list):
        """处理用户查询并生成建议"""
        # 获取对话历史
        conversation_history = self.memory.get_history(user_id)


        responses = {}
        for mbti_type in mbti_types:
            # 获取或创建 Agent
            if mbti_type not in self.active_agents:
                self.active_agents[mbti_type] = MBTIAdviceAgent(mbti_type,use_vector_db=False)

            # 生成建议
            advice = self.active_agents[mbti_type].generate_advice(
                query, conversation_history
            )

            responses[mbti_type] = advice

            # 记录到对话历史
            self.memory.add_message(user_id, mbti_type, advice, is_user=False)

        # 返回json格式
        """
        {
            "INTJ": "INTJ风格的建议...",
            "ENFP": "ENFP风格的建议..."
        }
        """
        return responses


    # 追问函数
    """
    {
        "user_id": "user123",
        "query": "@INTJ 你能具体说说长期规划吗？"
    }
    """
    def process_followup(self, user_id: str, query: str, mbti_targets: list = None):
        """处理用户的追问"""
        # 如果没有指定目标，默认回复给所有人
        if not mbti_targets:
            mbti_targets = list(self.active_agents.keys())

        # 提取@信息
        if query.startswith("@"):
            # 解析@的MBTI类型
            parts = query.split(" ", 1)
            at_part = parts[0].replace("@", "")
            mentioned_types = at_part.split(",")

            # 如果指定了MBTI类型，则只对这些类型回复
            if mentioned_types and all(t in self.active_agents for t in mentioned_types):
                mbti_targets = mentioned_types
                query = parts[1] if len(parts) > 1 else ""

        # 记录用户追问到对话历史
        self.memory.add_message(user_id, "用户", query, is_user=True)

        # 返回json格式
        """
        {
            "INTJ": "INTJ的追问回复..."
        }
        """
        # 处理追问
        return self.process_user_query(user_id, query, mbti_targets)


# 测试用的主函数
if __name__ == "__main__":
    system = MBTIAdviceSystem(use_vector_db=False)

    # 用户第一次提问
    user_id = "user123"
    initial_query = "帮我想想今天晚上吃什么吧。"
    mbti_types = ["ENFJ", "ENFP" ,"ESFJ"]

    responses = system.process_user_query(user_id, initial_query, mbti_types)
    for mbti, response in responses.items():
        print(f"{mbti}: {response}")

    # 用户追问

    # followup = "@INTJ 你提到的长期规划能具体说说吗？"
    while True:
        followup=input("请继续追问")
        followup_responses = system.process_followup(user_id, followup)
        for mbti, response in followup_responses.items():
            print(f"{mbti}: {response}")