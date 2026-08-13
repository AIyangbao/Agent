"""
Agent 运行时测试: stub 掉 LLM(get_llm) 和 curd 数据层, 专测 ReAct 循环
"该调工具时会不会调、调的是不是对的那个"。
不连真 LLM、不连库 —— 全内存跑。
"""
import pytest
from langchain_core.messages import AIMessage
import services.agent_service as agent_service
import tools.blog_tools as blog_tools

class FakeLLM:
    """按计划(plan)回放: 第一轮返回 tool_calls, 第二轮返回文本答案。"""
    def __init__(self, plan):
        # plan 元素: ("tool", 工具名, 参数字典) 或 ("answer", 文本)
        self._plan = plan
        self._i = 0

    async def ainvoke(self, messages, tools=None):
        step = self._plan[self._i]
        self._i += 1
        if step[0] == "tool":
            return AIMessage(
                content="",
                tool_calls=[{"name": step[1], "args": step[2], "id": f"call_{self._i}"}],
            )
        return AIMessage(content=step[1], tool_calls=[])

    async def stream(self, messages):
        # Answer 分支只走这里, 吐一个token 即可
        last = self._plan[self._i - 1]
        yield last[1] if last[0] == "answer" else " (回答)"

def _patch(monkeypatch, plan, tags=None, blogs=None):
        # 把 Agent 用的 get_llm 换成 FakeLLM
        monkeypatch.setattr(agent_service, "get_llm", lambda: FakeLLM(plan))
        # stub 工具的数据层
        if tags is not None:
           async def fake_tags(db):
            return tags
           monkeypatch.setattr(blog_tools, "get_tag_list", fake_tags)
        if blogs is not None:
            async def fake_blogs(db, limit=10):
                return blogs
            monkeypatch.setattr(blog_tools, "get_blog_list", fake_blogs)

async def test_asks_tags_triggers_list_blog_tags(monkeypatch):
        _patch(monkeypatch,
               plan=[("tool", "list_blog_tags", {}), ("answer", "标签有 Python、Docker")],
               tags=[{"id": 1, "name": "Python"}, {"id": 2, "name": "Docker"}])
        agent = agent_service.AgentService()
        out = [t async for t in agent.chat_stream("博客有哪些标签?", history=[])]
        text = "".join(out)
        # 工具被调了(结果进了最终回答), 且内容正确
        assert "Python" in text and "Docker" in text

async def test_asks_recent_triggers_list_recent_blogs(monkeypatch):
    from datetime import datetime
    class _B:
        def __init__(self):
            self.title = "我的第一篇"
            self.create_time = datetime(2026, 8, 13)
            self.tags_name = []
    _patch(monkeypatch,
           plan=[("tool", "list_recent_blogs", {"limit": 5}), ("answer", "最近发了《我的第一篇》")],
           blogs=[_B()])
    agent = agent_service.AgentService()
    out = [t async for t in agent.chat_stream("最近发了哪些博客?", history=[])]
    assert "我的第一篇" in "".join(out)

async def test_no_tool_call_for_plain_chat(monkeypatch):
    # 普通闲聊不该触发任何工具(第一轮就直接 answer)
    _patch(monkeypatch, plan=[("answer", "你好呀")], tags=[], blogs=[])
    agent = agent_service.AgentService()
    out = [t async for t in agent.chat_stream("你好", history=[])]
    assert "你好呀" in "".join(out)