"""HyperLogLog UV 统计测试（Redis 练习第 4 块）。

运行:  pytest tests/test_uv.py -v
前置:  本机 Redis 可达；不可达时用例自动 skip。
说明:  uv_service 用「早绑定 redis_client」(与 redis_lock / blog_cache 一致)，
      conftest 的 redis_isolated 需把 uv_service.redis_client 也指向测试 client (db=1)。
"""
import asyncio
import pytest
import config.cache_conf as cache_conf
from services.uv_service import record_uv, count_uv


async def _redis_ok() -> bool:
    rc = cache_conf.redis_client
    if rc is None:
        return False
    try:
        await asyncio.wait_for(rc.ping(), timeout=2)
        return True
    except Exception:
        return False


async def _flush_uv():
    rc = cache_conf.redis_client
    keys = await rc.keys("uv:blog:*")
    if keys:
        await rc.delete(*keys)


async def test_record_dedup_and_count():
    """同一 value 多次记录只算 1 个 UV;不同 value 各算 1 个(HLL 自动去重）。"""
    if not await _redis_ok():
        pytest.skip("本机 Redis 未运行，跳过 UV 测试")
    key = "uv:blog:111"
    await _flush_uv()
    try:
        await record_uv(key, "1.1.1.1")
        await record_uv(key, "1.1.1.1")          # 重复，应被去重
        assert await count_uv(key) == 1
        await record_uv(key, "2.2.2.2")
        assert await count_uv(key) == 2
    finally:
        await _flush_uv()


async def test_count_missing_key_returns_zero():
    """查询不存在的 key,PFCOUNT 返回 0(不为 None,不报错）。"""
    if not await _redis_ok():
        pytest.skip("本机 Redis 未运行，跳过 UV 测试")
    assert await count_uv("uv:blog:999999") == 0


async def test_uv_endpoint_reflects_count(auth_client_a):
    """GET /api/blogs/uv 返回的 blog_uv 与真实计数一致。"""
    if not await _redis_ok():
        pytest.skip("本机 Redis 未运行，跳过 UV 测试")
    key = "uv:blog:222"
    await _flush_uv()
    try:
        await record_uv(key, "9.9.9.9")
        resp = await auth_client_a.get("/api/blogs/uv", params={"id": 222})
        assert resp.status_code == 200
        assert resp.json()["data"]["blog_uv"] == 1
    finally:
        await _flush_uv()
