import redis.asyncio as redis
import json
from typing import Any
from config.settings import settings

# 创建 Redis 的连接对象
redis_client = redis.Redis(
    host=settings.REDIS_HOST,  # Redis 服务器的主机地址
    port=settings.REDIS_PORT,  # Redis 端口号
    db=settings.REDIS_DB,  # Redis 数据库编号, 0~15
    decode_responses=True,  # 是否将子杰数据解码为字符串
)

# 设置 和 读取 (字符串 和 列表或字典)"[{}]"


# 读取: 字符串
async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败:{e}")
        return None


# 读取: 列表或字典
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"获取JSON缓存失败:{e}")
        return None


# 设置缓存 setex(key,expire,value)
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            # 转字符串再存
            value = json.dumps(value, ensure_ascii=False)  # 中文正常保存
        await redis_client.setex(key, expire, value)
        return None
    except Exception as e:
        print(f"设置缓存失败:{e}")
        return False

# 删除缓存 delex(key)
async def delete_cache(key: str):
    try:
        return await redis_client.delete(key)
    except Exception as e:
        print(f"删除缓存失败:{e}")
        return False

# 删除所有prefix*的key,用于列表缓存批量失效
async def clear_prefix(prefix: str):
    try:
        keys = [k async for k in redis_client.scan_iter(match=f"{prefix}")]
        if keys:
            await redis_client.delete(*keys)
        return len(keys)
    except Exception as e:
        print(f"清前缀缓存失败:{e}")
        return 0