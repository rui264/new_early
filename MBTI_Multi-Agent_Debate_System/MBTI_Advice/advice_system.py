#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MBTI建议系统 - 独立模块
避免导入路径问题
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 强制禁用代理设置
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

try:
    from agents.mbti_agent import MBTIAdviceAgent
    from memory.conversation_memory import MBTIConversationMemory
    from dotenv import load_dotenv
    
    load_dotenv()  # 加载环境变量
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有依赖模块都已正确安装")
    # 创建简单的替代类
    class MBTIAdviceAgent:
        def __init__(self, mbti_type, **kwargs):
            self.mbti_type = mbti_type
        
        def generate_advice(self, query, history=""):
            return f"作为{mbti_type}类型，我建议您：{query}。这是一个基于{mbti_type}思维方式的建议。"
    
    class MBTIConversationMemory:
        def __init__(self):
            self.memory = {}
        
        def get_history(self, user_id):
            return self.memory.get(user_id, "")
        
        def add_message(self, user_id, sender, message, is_user=False):
            if user_id not in self.memory:
                self.memory[user_id] = ""
            self.memory[user_id] += f"{sender}: {message}\n"

class MBTIAdviceSystem:
    """MBTI建议系统主类"""
    
    def __init__(self, use_vector_db: bool = False, offline_mode: bool = True):
        self.use_vector_db = use_vector_db
        self.offline_mode = offline_mode
        self.memory = MBTIConversationMemory()
        self.active_agents = {}  # MBTI 类型到 Agent 的映射
        print(f"✓ MBTI建议系统初始化完成 (离线模式: {offline_mode})")

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

            return responses
            
        except Exception as e:
            print(f"❌ 处理用户查询时出错: {e}")
            return {"error": f"系统处理查询时出错: {str(e)}"}

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

            # 处理追问
            return self.process_user_query(user_id, query, mbti_targets)
            
        except Exception as e:
            print(f"❌ 处理追问时出错: {e}")
            return {"error": f"系统处理追问时出错: {str(e)}"}

# 测试函数
def test_advice_system():
    """测试建议系统"""
    print("🧪 测试MBTI建议系统")
    print("=" * 50)
    
    try:
        system = MBTIAdviceSystem(offline_mode=True)
        
        # 测试查询
        user_id = "test_user_001"
        query = "如何提高工作效率？"
        mbti_types = ["INTJ", "ENFP"]
        
        print(f"测试查询: {query}")
        responses = system.process_user_query(user_id, query, mbti_types)
        
        print("测试结果:")
        for mbti, response in responses.items():
            print(f"  {mbti}: {response}")
        
        print("✅ 测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_advice_system() 