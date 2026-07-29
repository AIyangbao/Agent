"""博客缓存服务：封装 Cache-Aside 读穿透、防穿透、防雪崩与写后失效。
路由层只调用这里的语义化函数，不直接碰 Redis key / TTL / 哨兵。
"""
from typing import Optional

from fastapi.encoders import jsonable_encoder
from config.cache_conf import (
    get_json_cache,
    set_cache,
    delete_cache,
    clear_prefix,
    jitter_ttl,
    NONE_SENTINEL,
    PENETRATION_TTL,
)

LIST_PREFIX = "blog:list:"
DETAIL_PREFIX = "blog:detail:"

# ===== key 构建 =====
def build_list_key(tag_id: Optional[int], keyword: Optional[str], page: int,page_size: int) -> str:
    return f"{LIST_PREFIX}{tag_id}:{keyword}:{page}:{page_size}"

def build_detail_key(blog_id: int) -> str:
    return f"{DETAIL_PREFIX}{blog_id}"

# ===== 列表: 读穿透 + 写回 =====
async def get_cached_blog_list(key: str):
    return await get_json_cache(key)

async def set_cached_blog_list(key: str, data) -> None:
     # data 可能含 ORM/Row，先 jsonable_encoder 成纯 dict 再存
     await set_cache(key, jsonable_encoder(data), expire=jitter_ttl())

# ===== 详情: 读穿透 + 防穿透 + 写回 =====
async def get_cached_blog_detail(blog_id: int):
    """返回缓存数据；未命中返回 None;命中防穿透哨兵返回字符串 'NONE'。"""
    cached = await get_json_cache(build_detail_key(blog_id))
    if cached is None:
        return None
    if cached == NONE_SENTINEL:
        return "NONE"
    return cached

async def set_cached_blog_detail(blog_id: int, blog) -> None:
    await set_cache(build_detail_key(blog_id), jsonable_encoder(blog),expire=jitter_ttl())

async def set_blog_detail_none(blog_id: int) -> None:
    """DB 查不到时写防穿透哨兵（短 TTL)."""
    await set_cache(build_detail_key(blog_id),NONE_SENTINEL, expire=PENETRATION_TTL)

# ===== 写后失效 =====
async def invalidate_blog_list() -> None:
    """列表组合不可枚举，统一按前缀清空。"""
    await clear_prefix(LIST_PREFIX)

async def invalidate_blog_detail(blog_id: int) -> None:
    await delete_cache(build_detail_key(blog_id))


