"""博客缓存路由集成测试：走真实 HTTP,验证端到端缓存命中/防穿透/写后失效。
运行: pytest tests/test_blog_cache_integration.py -v
前置: 本地 Redis 在 localhost:6379
"""
import pytest
from httpx import AsyncClient

from services.blog_cache import (
    build_list_key,
    get_cached_blog_detail,
    get_cached_blog_list,
)
from config.cache_conf import clear_prefix

async def _clear_cache():
     """隔离缓存（不碰 DB,DB 由 conftest 的 setup_db 管）。"""
     await clear_prefix("blog_list:")
     await clear_prefix("blog:detail:")

class TestBlogCacheIntegration():
    async def test_list_second_hit_is_cached(self, client: AsyncClient):
      """列表第一次回源、第二次命中缓存（message 带 '缓存'）。"""
      await _clear_cache()
      r1 = await client.get("/api/blogs/list_blogs?page=1&pageSize=10")
      assert r1.status_code == 200
      assert "缓存" not in r1.json()["message"]

      r2 = await client.get("/api/blogs/list_blogs?page=1&pageSize=10")
      assert r2.status_code == 200
      assert "缓存" in r2.json()["message"]
      # Redis 里确有这个列表 key
      key = build_list_key(None, None, 1, 10)
      assert await get_cached_blog_list(key) is not None
    
    async def test_detail_second_hit_is_cached(self, auth_client_a: AsyncClient):
        """发一篇后，详情第一次回源、第二次命中缓存。"""
        await _clear_cache()
        add = await auth_client_a.post(
            "/api/blogs/add",
            json={"title": "缓存集成测试", "content": "正文", "tag_ids": [1]},
        )
        assert add.status_code == 200
        bid = add.json()["data"]["id"]

        r1 = await auth_client_a.get(f"/api/blogs/detail?id={bid}")
        assert r1.status_code == 200
        assert "缓存" not in r1.json()["message"]

        r2 = await auth_client_a.get(f"/api/blogs/detail?id={bid}")
        assert r2.status_code == 200
        assert "缓存" in r2.json()["message"]
    
    async def test_detail_penetration_sentinel(self, client: AsyncClient):
        """不存在的 id:两次都 404,且第二次命中防穿透哨兵(不再查库)."""
        await _clear_cache()
        r1 = await client.get("/api/blogs/detail?id=999999")
        assert r1.status_code == 404
        r2 = await client.get("/api/blogs/detail?id=999999")
        assert r2.status_code == 404
        # 哨兵已落盘：直接读缓存确认是 "NONE"
        assert await get_cached_blog_detail(999999) == "NONE"
    
    async def test_write_invalidates_list_cache(self, auth_client_a: AsyncClient):
        """新增博客后，列表缓存被清空（写后失效）。"""
        await _clear_cache()
        # 先建立列表缓存
        await auth_client_a.get("/api/blogs/list_blogs?page=1&pageSize=10")
        key = build_list_key(None, None, 1, 10)
        assert await get_cached_blog_list(key) is not None

        # 新增一篇 -> 应触发 invalidate_blog_list()
        add = await auth_client_a.post(
            "/api/blogs/add",
            json={"title": "触发失效的文章","content": "内容", "tag_ids": [2]},
        )
        assert add.status_code == 200
        assert await get_cached_blog_list(key) is None