from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import BaseMessage
from llm.base import BaseLLM

"""千问LLM实现"""

class QwenLLM(BaseLLM):
    """封装ChatTongyi,支持function calling"""

    def __init__(self,model: str = 'qwen-plus',api_key: str = ""):
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY未设置")
        self._llm = ChatTongyi(
            model=model,
            dashscope_api_key=api_key,
            temperature=0.7,
            streaming=True,
        )
    
    def invoke(self,messages: list[BaseMessage],tools:list[dict] | None = None):
        llm= self._llm
        if tools:
            llm = llm.bind_tools(tools)
        return llm.invoke(messages)
    async def stream(self, messages: list[BaseMessage], tools: list[dict] | None = None):
        llm = self._llm
        if tools:
            llm = llm.bind_tools(tools)
        async for chunk in llm.astream(messages):
            if chunk.content:
                yield chunk.content