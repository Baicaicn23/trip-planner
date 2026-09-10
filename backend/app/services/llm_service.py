"""LLM服务模块 —— DeepSeek 的专属接线员（全项目共用一个AI账号）"""

from hello_agents import HelloAgentsLLM
from ..config import get_settings

# 全局LLM实例
_llm_instance = None


def get_llm() -> HelloAgentsLLM:
    """获取LLM实例(单例模式) —— 全项目共享一个DeepSeek客户端

    【干什么用】首次调用创建 HelloAgentsLLM（自动读 .env 里 LLM_API_KEY 等配置），
    之后四位AI专员全部共用这一个客户端。
    【类比】公司只办一个AI企业账号：开通一次全组共用——不重复建、好控额度。

    Returns:
    
    Returns:
        HelloAgentsLLM实例
    """
    global _llm_instance
    
    if _llm_instance is None:
        settings = get_settings()
        
        # HelloAgentsLLM会自动从环境变量读取配置
        # 包括OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL等
        _llm_instance = HelloAgentsLLM()
        
        print(f"✅ LLM服务初始化成功")
        print(f"   提供商: {_llm_instance.provider}")
        print(f"   模型: {_llm_instance.model}")
    
    return _llm_instance


def reset_llm():
    """重置LLM实例(用于测试或重新配置)"""
    global _llm_instance
    _llm_instance = None

