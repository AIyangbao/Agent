from config.cache_conf import redis_client

async def record_uv(key: str, value: str) -> None:
    """PFADD:自动去重,value 相同不会重复计数。"""
    await redis_client.pfadd(key, value)

async def count_uv(key: str) -> int:
    """PFCOUNT:返回基数估算值。"""
    return await redis_client.pfcount(key)
