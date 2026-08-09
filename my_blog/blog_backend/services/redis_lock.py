import asyncio
import uuid
from config.cache_conf import redis_client
from utils.log import logger
from fastapi import HTTPException

_RELEASE_LUA = (
    "if redis.call('get', KEYS[1]) == ARGV[1] "
    "then return redis.call('del', KEYS[1]) "
    "else return 0 end"
)

class RedisLock:
    def __init__(self, name: str, expire: int = 10, retry: int = 3, retry_delay: float
                 = 0.1):
        self.name = f"lock:{name}"
        self.expire = expire
        self.token = uuid.uuid4().hex # 每个锁实例唯一, 用于安全释放
        self.retry = retry
        self.retry_delay = retry_delay
        self._watchdog = None


    async def acquire(self) -> bool:
        for _ in range(self.retry):
            ok = await redis_client.set(self.name, self.token, nx=True, ex=self.expire)
            if ok:
               self._start_watchdog()
               return True
            await asyncio.sleep(self.retry_delay)
        return False

    def _start_watchdog(self):
        """看门狗: 每 expire/2 秒 续期一次, 直到锁释放或 token 不匹配"""
        async def _tick():
            try:
                while True:
                    await asyncio.sleep(self.expire / 2)
                    if await redis_client.get(self.name) == self.token:
                        await redis_client.expire(self.name, self.expire)
                    else:
                        break
            except asyncio.CancelledError:
                pass
        self._watchdog = asyncio.create_task(_tick())

    async def release(self):
        if self._watchdog:
            self._watchdog.cancel()
        try:
            await redis_client.eval(_RELEASE_LUA, 1, self.name, self.token)
        except Exception as e:
            logger.warning("释放锁失败:%s", e)

class RedisLockCtx:
    """异步上下文管理器, 用法更优雅:
    async with RedisLockCtx('order: 123) as lock:
        if not lock: raise HTTPException(429, '操作过于频繁)
        ...临界区...
    """
    def __init__(self, name, **kw):
        self._lock = RedisLock(name, **kw)

    async def __aenter__(self):
        ok = await self._lock.acquire()
        return self._lock if ok else None

    async def __aexit__(self, *exc):
        await self._lock.release()

