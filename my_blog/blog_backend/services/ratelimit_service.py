"""通用爆破防护：基于 Redis 的失败计数 + 临时锁定。复用 config.cache_conf 引擎。"""
from config.cache_conf import set_cache, get_cache, delete_cache

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