"LLM工厂 -- 根据配置创建实例,调用方不关心具体实现"

from config.settings import settings
from llm.qwen import QwenLLM

def get_llm() -> QwenLLM:
    "从 settings 读取参数创建LLM实例"
    if not settings.DASHSCOPE_API_KEY:
        raise RuntimeError("DASHSCOPE_API_KEY 未配置,请在.env中设置")
    return QwenLLM(
        model=settings.QWEN_MODEL or "qwen-plus",
        api_key=settings.DASHSCOPE_API_KEY,
    )