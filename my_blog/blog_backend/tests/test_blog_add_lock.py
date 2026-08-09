"""add 接口分布式锁测试：验证「防同一用户并发重复提交」。

运行:  pytest tests/test_blog_add_lock.py -v
前置:  本机 Redis 可达；不可达时用例自动 skip。
注意:  conftest 已把 redis_lock / blog_cache 的 redis_client 都指向测试 client (db=1),
       所以本文件手动占锁也必须用「动态访问 cache_conf.redis_client」(=db=1),
       不能用 `from config.cache_conf import redis_client` 早绑定（那是 db=0 旧单例）。
"""
import asyncio
import pytest
from httpx import AsyncClient
import config.cache_conf as cache_conf #  动态访问，跟 conftest 覆盖后的 db=1 测试 client 一致

async def _redis_ok() -> bool:
    rc = cache_conf.redis_client
    if rc is None:
        return False
    try:
        await asyncio.wait_for(rc.ping(), timeout=2)
        return True
    except Exception:
        return False

async def test_add_returns_429_when_lock_held(auth_client_a: AsyncClient):
    """锁被占用时,add 接口必须拒绝(429),不能放行第二个并发提交。"""
    if not await _redis_ok():
        pytest.skip("本机Redis未运行, 跳过锁测试")

    me = await auth_client_a.get("/api/user/me")
    uid = me.json()["data"]["id"]
    lock_key = f"lock:add_blog:{uid}"
    rc = cache_conf.redis_client

    try:
        ok = await rc.set(lock_key, "blocker-token", nx=True, ex=30)
        assert ok, "预占锁失败(db 里可能已有残留 key)"

        resp = await auth_client_a.post(
            "/api/blogs/add",
            json={"title": "并发重复提交", "content": "应被拦截", "tag_ids":[1]},
        )
        assert resp.status_code == 429
        # 项目统一响应包装是 {code, message, data}，429 文案在 message 字段
        assert "频繁" in resp.json().get("message", "")
    finally:
        await rc.delete(lock_key) # 清理, 避免污染

async def test_add_success_when_lock_free(auth_client_a: AsyncClient):
    """锁空闲时,add 接口正常成功(200)——锁不能误伤正常请求。"""
    if not await _redis_ok():
        pytest.skip("本机Redis 未运行, 跳过锁测试")

    resp = await auth_client_a.post(
        "/api/blogs/add",
        json={"title": "锁空闲正常发", "content": "应当成功", "tag_ids": [1]},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["title"] == "锁空闲正常发"
    