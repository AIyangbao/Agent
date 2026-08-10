"""LLM抽象接口 -- 方便以后换模型(Qwen -> DeepSeek -> OpenAI)"""

from abc import ABC,abstractmethod
from typing import Any

class BaseLLM(ABC):

    @abstractmethod
    async def ainvoke(self,messages: list[Any], tools: list[dict] | None = None) -> Any:
        """
        调用LLM
        messages: LangChain消息列表
        tools: 可选,函数调用schema
        返回:LangChain AIMessage
        """
    
    @abstractmethod
    def stream(self,messages: list[Any], tools: list[dict] | None = None):
        """
        流式输出,逐 token yield (str)。 实现可以是 async generator 。
        """