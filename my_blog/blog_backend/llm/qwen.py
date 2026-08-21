from langchain_openai import ChatOpenAI
from config.settings import settings

class QwenLLM:
    """DashScope OpenAI 兼容模式 LLM 客户端，支持 qwen3.8-max 等最新模型"""
    def __init__(self, model: str | None = None, **kwargs):
        kwargs.pop("api_key", None)   # factory 可能传 api_key，丢弃，统一从 settings 取
        self._llm = ChatOpenAI(
            model=model or settings.QWEN_MODEL,
            api_key=settings.DASHSCOPE_API_KEY,
            base_url=settings.DASHSCOPE_BASE_URL,
            streaming=True,
            **kwargs,
        )

    async def ainvoke(self, messages, **kwargs):
        return await self._llm.ainvoke(messages, **kwargs)

    async def stream(self, messages, **kwargs):
        # agent_service.py:128 用 `async for token in self._llm.stream(...)`，
        # routers/ai.py:49 再对 token 做 json.dumps({'reply': token}) ——
        # 整条链路要求 stream 产出【字符串】，故这里取 chunk.content 再 yield。
        #（旧 ChatTongyi 时代的 QwenLLM.stream 也是这么转的，保持契约一致）
        async for chunk in self._llm.astream(messages, **kwargs):
            content = chunk.content
            if isinstance(content, list):   # 多模态 content 块兜底
                content = "".join(
                    p.get("text", "") if isinstance(p, dict) else str(p)
                    for p in content
                )
            yield content