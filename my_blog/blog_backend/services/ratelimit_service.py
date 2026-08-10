"""通用爆破防护：基于 Redis 的失败计数 + 临时锁定。复用 config.cache_conf 引擎。"""
from config.cache_conf import set_cache, get_cache, delete_cache, redis_client

FAIL_TTL = 600 # 计数/锁定窗口10分钟
MAX_FAIL = 5 # 失败5次锁定

async def is_locked(key: str) -> bool:
    return await get_cache(f"lock:{key}") is not None

async def record_fail(key: str) -> int:
    fk = f"fail:{key}"
    n = int(await get_cache(fk) or 0) + 1
    await set_cache(fk, str(n), expire=FAIL_TTL)
    if n >= MAX_FAIL:
        await set_cache(f"lock:{key}","1",expire=FAIL_TTL)
        await delete_cache(fk)
    return n

AI_RATE_LIMIT = 20 # 每用户每分钟最多 20 条 AI 消息
AI_RATE_WINDOW = 60 # 窗口 60 秒

async def ai_rate_limited(user_id: int) -> bool:
    """固定窗口限流: True=已超理应拒绝。Redis 挂了放行(降级保可用)。"""
    key = f"rl:ai:{user_id}"
    try:
        n = await redis_client.incr(key) # INCR 原子自增, 无并发竞争
        if n == 1:
            await redis_client.expire(key, AI_RATE_WINDOW) # 窗口内第一次才设过期
        return n > AI_RATE_LIMIT
    except Exception:
        return False # Redis 异常 → 不限流, 别把服务搞挂