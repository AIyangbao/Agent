"""博客工具单元测试:stub 掉 curd 数据层, 专测 execute 的拼装/边界逻辑, 不连库。"""
from datetime import datetime
import pytest
import tools.blog_tools as blog_tools

# ===== ListTagsTool =====
async def test_list_tags_with_data(monkeypatch):
    async def fake(db):
        return [{"id":1, "name": "Python"}, {"id": 2, "name": "Docker"}]
    monkeypatch.setattr(blog_tools, "get_tag_list", fake)
    result = await blog_tools.ListTagsTool().execute()
    assert "个标签" in result and "Python" in result and "Docker" in result

async def test_list_tags_empty(monkeypatch):
    async def fake(db):
        return []
    monkeypatch.setattr(blog_tools, "get_tag_list", fake)
    assert "暂无" in await blog_tools.ListTagsTool().execute()

# ===== RecentBlogsTool =====
class _FakeBlog: # 工具只用 title/create_time/tags_name 三个属性, 模拟即可
    def __init__(self, title, create_time=None, tags_name=None):
        self.title = title
        self.create_time = create_time
        self.tags_name = tags_name or []

async def test_recent_blogs_formats(monkeypatch):
    async def fake(db, limit=10):
        return [_FakeBlog("第一篇", datetime(2026, 8, 13), ["Docker"])]
    monkeypatch.setattr(blog_tools, "get_blog_list", fake)
    result = await blog_tools.RecentBlogsTool().execute(limit=5)
    assert "第一篇" in result and "2026-08-13" in result and "Docker" in result

async def test_recent_blogs_empty(monkeypatch):
    async def fake(db, limit=10):
        return []
    monkeypatch.setattr(blog_tools, "get_blog_list", fake)
    assert "还没有发布" in await blog_tools.RecentBlogsTool().execute()

async def test_recent_blogs_limit_clamped(monkeypatch):
    captured = {}
    async def fake(db, limit=10):
        captured["limit"] = limit
        return []
    monkeypatch.setattr(blog_tools, "get_blog_list", fake)
    await blog_tools.RecentBlogsTool().execute(limit=9999)
    assert captured["limit"] == 3

async def test_get_blog_stats(monkeypatch):
    async def fake_count(db):
        return 42
    async def fake_uv(k):
        return 128
    monkeypatch.setattr(blog_tools, "get_list_count", fake_count)
    monkeypatch.setattr(blog_tools, "count_uv", fake_uv)
    agent = blog_tools.BlogStatsTool()
    res = await agent.execute()
    assert "篇文章" in res and "128" in res