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
    redis_client,
)
from curd.blogs import get_blog_detail
from utils.log import logger
import asyncio
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

LOCK_PREFIX = "blog:lock:detail:"
LOCK_TTL = 5 # 锁超时(秒), 必须 > 差DB 耗时, 否则会误放多个请求

async def _acquire_detail_lock(blog_id: int) -> bool:
    """SET key token NX EX -- 原子加锁, 拿到返回True"""
    return await redis_client.set(
        f"{LOCK_PREFIX}{blog_id}","1", nx=True, ex=LOCK_TTL
    ) is not None

async def _release_detail_lock(blog_id: int) -> None:
    await redis_client.delete(f"{LOCK_PREFIX}{blog_id}")

async def get_blog_detail_with_mutex(blog_id: int, db):
    """带互斥锁的详情读取: 缓存未命中只放一个请求查DB"""
    # 先查缓存(穿透/雪崩已处理)
    cached = await get_cached_blog_detail(blog_id)
    if cached is not None:
        return cached

    # 缓存未命中 -> 抢锁
    got_lock = await _acquire_detail_lock(blog_id)
    if not got_lock:
        # —— 等待者分支：自旋等到锁消失，全程只查缓存，绝不查 DB ——
        # 自旋总时长必须 >= 锁 TTL，确保能等到锁释放 / 自然过期。
        # 绝不能写成 "自旋 5 次×50ms=250ms 就放弃然后查 DB"：
        #   若锁 TTL=5 秒，250ms << 5 秒，大量等待者会在锁还活着时提前放弃，
        #   全部 fall through 去查 DB → 瞬间打穿，锁形同虚设。
        waited = 0.0
        while waited < LOCK_TTL + 0.5:
            await asyncio.sleep(0.05)
            waited += 0.05
            if not await redis_client.exists(f"{LOCK_PREFIX}{blog_id}"):
              #  锁没了：持锁者已主动释放（重建完成）或超时过期
                cached = await get_cached_blog_detail(blog_id)
            if cached is not None:
                return cached # 真值或NONE都认
            # 缓存仍空：持锁者 DB 超时没写好（锁已过期），
            # 由本等待者顶上抢锁重建（依然只有 1 个查 DB），不自己
            # 直接查DB
            if await _acquire_detail_lock(blog_id):
                got_lock = True
                break
            # 没抢到（被别的等待者抢了）→ 继续等下一轮
        if not got_lock:
            # 真极端：等满整个锁周期仍没建好，降级返回 NONE，绝不查 DB
            return "NONE"

    

    # 拿到锁 -> 双重检查(避免抢锁瞬间别人已重建)
    try:
        cached = await get_cached_blog_detail(blog_id)
        if cached is not None:
            return cached
        try:
            blog = await get_blog_detail(db, blog_id)
        except Exception:
            logger.warning("blog %s 查DB超时/异常, 降级返回NONE",blog_id)
            return "NONE"
        if blog is None:
            await set_blog_detail_none(blog_id)
            return "NONE"
        await set_cached_blog_detail(blog_id, blog)
        return blog
    finally:
        await _release_detail_lock(blog_id)


