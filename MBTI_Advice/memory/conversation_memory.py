from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage


class MBTIConversationMemory:
    def __init__(self):
        # 为每个用户创建一个对话历史
        self.user_memories = {}

    def get_memory(self, user_id: str) -> ConversationBufferMemory:
        """获取用户的对话记忆"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = ConversationBufferMemory(
                return_messages=True, memory_key="chat_history"
            )
        return self.user_memories[user_id]

    def add_message(self, user_id: str, mbti_type: str, message: str, is_user: bool):
        """添加消息到对话历史"""
        memory = self.get_memory(user_id)
        role = "用户" if is_user else mbti_type
        message_obj = HumanMessage(content=f"[{role}] {message}") if is_user else \
            AIMessage(content=f"[{mbti_type}] {message}")

        memory.chat_memory.add_message(message_obj)

    def get_history(self, user_id: str) -> str:
        """获取用户的对话历史文本"""
        memory = self.get_memory(user_id)
        messages = memory.chat_memory.messages
        return "\n".join([f"{msg.type}: {msg.content}" for msg in messages])