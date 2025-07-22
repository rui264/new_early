#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本
验证所有模块是否正常工作
"""

import sys
import os

def test_imports():
    """测试导入是否正常"""
    print("🧪 测试模块导入...")
    
    try:
        # 测试用户数据库模块
        print("  📦 测试 user_database 模块...")
        from user_database import SessionLocal, engine, Base
        print("    ✅ user_database 导入成功")
        
        # 测试MBTI辩论模块
        print("  📦 测试 MBTI_Debate 模块...")
        from MBTI_Debate.constants import MBTI_TYPES
        from MBTI_Debate.core.debate_engine import DebateEngine
        from MBTI_Debate.core.debate_manager import DebateManager
        print("    ✅ MBTI_Debate 导入成功")
        
        # 测试MBTI建议模块
        print("  📦 测试 MBTI_Advice 模块...")
        from MBTI_Advice.advice_system import MBTIAdviceSystem
        print("    ✅ MBTI_Advice 导入成功")
        
        # 测试FastAPI相关模块
        print("  📦 测试 FastAPI 模块...")
        from fastapi import FastAPI
        print("    ✅ FastAPI 导入成功")
        
        print("🎉 所有模块导入成功！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_database():
    """测试数据库连接"""
    print("\n🗄️ 测试数据库连接...")
    
    try:
        from user_database import SessionLocal, engine
        from user_database import Base
        
        # 创建表
        Base.metadata.create_all(bind=engine)
        print("  ✅ 数据库表创建成功")
        
        # 测试会话
        db = SessionLocal()
        try:
            # 简单的数据库操作测试
            result = db.execute("SELECT 1").scalar()
            print(f"  ✅ 数据库连接测试成功: {result}")
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 数据库测试失败: {e}")
        return False

def test_advice_system():
    """测试建议系统"""
    print("\n💡 测试建议系统...")
    
    try:
        from MBTI_Advice.advice_system import MBTIAdviceSystem
        
        # 创建建议系统实例
        system = MBTIAdviceSystem(offline_mode=True)
        print("  ✅ 建议系统初始化成功")
        
        # 测试建议生成
        user_id = "test_user_001"
        query = "如何提高工作效率？"
        mbti_types = ["INTJ", "ENFP"]
        
        responses = system.process_user_query(user_id, query, mbti_types)
        print(f"  ✅ 建议生成成功，获得 {len(responses)} 个建议")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 建议系统测试失败: {e}")
        return False

def test_mbti_types():
    """测试MBTI类型"""
    print("\n🎭 测试MBTI类型...")
    
    try:
        from MBTI_Debate.constants import MBTI_TYPES
        
        print(f"  📋 可用的MBTI类型: {len(MBTI_TYPES)} 个")
        print(f"  📝 类型列表: {list(MBTI_TYPES)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ MBTI类型测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始系统测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("数据库连接", test_database),
        ("建议系统", test_advice_system),
        ("MBTI类型", test_mbti_types),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 测试: {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} 测试通过")
        else:
            print(f"❌ {test_name} 测试失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常启动")
        print("\n💡 下一步:")
        print("  1. 运行: uvicorn main:app --reload")
        print("  2. 打开浏览器访问: http://localhost:8000")
        print("  3. 查看API文档: http://localhost:8000/docs")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 