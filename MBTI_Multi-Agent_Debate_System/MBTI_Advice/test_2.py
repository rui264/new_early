from agents.mbti_agent import MBTIAdviceAgent
from memory.conversation_memory import MBTIConversationMemory
import os
from dotenv import load_dotenv

load_dotenv()  # 加载环境变量

# 强制禁用代理设置，确保安全运行
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

class MBTIAdviceSystem:
    def __init__(self, use_vector_db: bool = False, offline_mode: bool = True):
        self.use_vector_db = use_vector_db
        self.offline_mode = offline_mode
        self.memory = MBTIConversationMemory()
        self.active_agents = {}  # MBTI 类型到 Agent 的映射
        print(f"✓ MBTI建议系统初始化完成 (离线模式: {offline_mode})")

    # 首次提问函数
    def process_user_query(self, user_id: str, query: str, mbti_types: list):
        """处理用户查询并生成建议"""
        try:
            # 获取对话历史
            conversation_history = self.memory.get_history(user_id)

            responses = {}
            for mbti_type in mbti_types:
                try:
                    # 获取或创建 Agent
                    if mbti_type not in self.active_agents:
                        print(f"🤖 创建 {mbti_type} Agent...")
                        self.active_agents[mbti_type] = MBTIAdviceAgent(
                            mbti_type, 
                            use_vector_db=self.use_vector_db,
                            offline_mode=self.offline_mode
                        )

                    # 生成建议
                    print(f"💭 {mbti_type} 正在生成建议...")
                    advice = self.active_agents[mbti_type].generate_advice(
                        query, conversation_history
                    )

                    responses[mbti_type] = advice

                    # 记录到对话历史
                    self.memory.add_message(user_id, mbti_type, advice, is_user=False)
                    print(f"✅ {mbti_type} 建议生成完成")

                except Exception as e:
                    error_msg = f"{mbti_type} 生成建议时出错: {str(e)}"
                    print(f"❌ {error_msg}")
                    responses[mbti_type] = f"抱歉，{mbti_type} 暂时无法提供建议。请稍后再试。"

            # 返回json格式
            """
            {
                "INTJ": "INTJ风格的建议...",
                "ENFP": "ENFP风格的建议..."
            }
            """
            return responses
            
        except Exception as e:
            print(f"❌ 处理用户查询时出错: {e}")
            return {"error": f"系统处理查询时出错: {str(e)}"}


    # 追问函数
    """
    {
        "user_id": "user123",
        "query": "@INTJ 你能具体说说长期规划吗？"
    }
    """
    def process_followup(self, user_id: str, query: str, mbti_targets: list = None):
        """处理用户的追问"""
        try:
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
            
        except Exception as e:
            print(f"❌ 处理追问时出错: {e}")
            return {"error": f"系统处理追问时出错: {str(e)}"}


# 测试用的主函数
if __name__ == "__main__":
    print("🚀 启动MBTI建议系统（安全模式）")
    print("=" * 50)
    
    # 使用离线模式避免代理连接问题
    system = MBTIAdviceSystem(use_vector_db=False, offline_mode=True)

    # 用户第一次提问
    user_id = "user123"
    initial_query = "我现在在做一个基于langchain实现多模型交互的问答系统，你有什么好的选题吗"
    mbti_types = ["ENFJ", "ENFP" ,"INTJ","INFP"]

    print(f"\n🎯 初始查询: {initial_query}")
    responses = system.process_user_query(user_id, initial_query, mbti_types)
    
    print("\n" + "=" * 50)
    print("📋 建议结果:")
    print("=" * 50)
    
    for mbti, response in responses.items():
        print(f"\n🔹 {mbti} 的建议:")
        print(f"   {response}")
        print("-" * 30)

    # 用户追问
    print("\n💬 您可以继续追问（输入 'quit' 退出）:")
    while True:
        try:
            followup = input("\n请输入您的追问: ").strip()
            
            if followup.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 感谢使用MBTI建议系统！")
                break
            
            if not followup:
                continue
            
            followup_responses = system.process_followup(user_id, followup)
            
            print("\n📋 追问回复:")
            for mbti, response in followup_responses.items():
                print(f"\n🔹 {mbti}: {response}")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序被中断，感谢使用！")
            break
        except Exception as e:
            print(f"\n❌ 处理追问时出错: {e}")
            print("请重新输入您的追问")