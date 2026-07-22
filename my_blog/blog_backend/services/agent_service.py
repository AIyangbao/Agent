"""Agent 运行时 -- ReAct 循环: Think -> Act -> Observe -> Answer"""

from langchain_core.messages import SystemMessage, HumanMessage,AIMessage,ToolMessage

from tools.registry import ToolRegistry
from llm.factory import get_llm

SYSTEM_PROMPT = """你是[技术宅小窝]博客的AI助手.你可以使用工具来帮助用户.

规则:
1. 技术问题直接回答,需要代码时给出代码示例
2. 需要实时数据(如天气)时,调用对应工具
3. 回答简洁、准确
"""

class AgentService:
    """无状态 Agent -- 每次请求创建一个实例"""

    MAX_ITERATIONS = 5 # 最多循环 5轮, 防止死循环

    def __init__(self):
        self._llm = get_llm()
        self._tools = ToolRegistry.get_all()
        self._tool_map = {t.definition().name: t for t in self._tools}
    
    # 构建 tool schema(LangChain格式)
    def _build_tool_schemas(self) -> list[dict]:
        schemas = []
        for t in self._tools:
            d = t.definition()
            schemas.append({
                "type": "function",
                "function": {
                    "name": d.name,
                    "description": d.description,
                    "parameters": d.parameters,
                }
            })
        return schemas
    # ----------- 主入口 -------------
    async def chat(self,message: str, history: list[dict] | None = None) -> str:
        """
        处理一次对话.
        histroy: [{"role": "user"/"ai","content":"..."}]
        """
        messages = self._build_messages(message,history or [])
        tool_schemas = self._build_tool_schemas()

        for _ in range(self.MAX_ITERATIONS):
            # Think: 让LLM觉得是回答还是调用工具
            response = self._llm.invoke(messages,tools=tool_schemas or None)

            if not hasattr(response,"tool_calls") or not response.tool_calls:
                return response.content
            
            messages.append(response)
            for tc in response.tool_calls:
                tool_name = tc["name"]
                tool_args = tc["args"]
                tool = self._tool_map.get(tool_name)

                if tool:
                    result = await tool.execute(**tool_args)
                else:
                    result = f"未知工具: {tool_name}"
                
                messages.append(ToolMessage(content=result,tool_call_id=tc["id"]))
        return "抱歉,处理超时,请简化问题后重试"
    async def chat_stream(self, message: str, history: list[dict] | None = None,rag_context: str | None = None):
        messages = self._build_messages(message, history or [],rag_context)
        tool_schemas = self._build_tool_schemas()

        for _ in range(self.MAX_ITERATIONS):
            # Think: 决定回答还是调工具
            response = self._llm.invoke(messages, tools=tool_schemas or None)

            if response.tool_calls:
                # 工具分支: 先把结果拿回来,不流式
                messages.append(response) # 保留 tool_calls 上下文
                for tc in response.tool_calls:
                    tool = self._tool_map.get(tc["name"])
                    result = await tool.execute(**tc["args"]) if tool else f"未知工具: {tc['name']}"
                    messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))
                continue

            # Answer 分支: 逐 token 流式输出
            async for token in self._llm.stream(messages):
               yield token
            return
        yield "抱歉,处理超时,请简化问题后重试"
                


    
    def _build_messages(self,message: str, history: list[dict],rag_context: str | None = None) -> list:
        system_content = SYSTEM_PROMPT
        if rag_context: # 只有检索到内容注入
            system_content += (
                "\n\n---- 以下是与用户问题相关的博客文章片段,"
                "回答时请优先基于这些内容,并在结尾注明参考来源 ----\n"
                + rag_context
            )
        messages = [SystemMessage(content=system_content)]

        # 添加历史对话
        for msg in history:
            role = msg.get("role","")
            content = msg.get("content","")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant" or role == "ai":
                messages.append(AIMessage(content=content))
        
        # 添加当前用户消息
        messages.append(HumanMessage(content=message))
        return messages
    


    