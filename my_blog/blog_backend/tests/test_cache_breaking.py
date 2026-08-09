"""防缓存击穿测试:并发读同一个未缓存的博客详情,DB 只应被查询 1 次。

运行:  pytest tests/test_cache_breaking.py -v
前置:  本机 Redis 可达；不可达时用例自动 skip。
"""
import asyncio
import pytest
import config.cache_conf as cache_conf #  动态访问 db=1 测试 client
from services import blog_cache 

async def _redis_ok() -> bool:
    rc = cache_conf.redis_client
    if rc is None:
        return False
    try:
        await asyncio.wait_for(rc.ping(), timeout=2)
        return True
    except Exception:
        return False

async def test_breaking_only_one_db_query(monkeypatch):
    """并发 20 路查同一篇不存在的文章，断言 DB 只被查 1 次。"""
    if not await _redis_ok():
        pytest.skip("本机 Redis 未运行, 跳过击穿测试")

    bid = 777777
    counter = {"n": 0}

    async def fake_get_blog_detail(db, blog_id):
        counter["n"] += 1
        await asyncio.sleep(0.05)
        return None

    monkeypatch.setattr(blog_cache, "get_blog_detail", fake_get_blog_detail)
    await blog_cache.invalidate_blog_detail(bid)

    results = await asyncio.gather(*[
        blog_cache.get_blog_detail_with_mutex(bid, None) for _ in range(20)
    ])

    assert all(r == "NONE" for r in results)
    assert counter["n"] == 1, f"DB被查了{counter['n']}次, 互斥锁没生效!"