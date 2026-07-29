"""博客缓存服务层单元测试：纯 Redis 交互，不依赖 DB，跑得快。
运行: pytest tests/test_blog_cache.py -v
前置: 本地 Redis 在 localhost:6379（redis-cli ping -> PONG）
"""
from services.blog_cache import (
    build_list_key,
    build_detail_key,
    get_cached_blog_list,
    set_cached_blog_list,
    get_cached_blog_detail,
    set_cached_blog_detail,
    set_blog_detail_none,
    invalidate_blog_list,
    invalidate_blog_detail,
)
from config.cache_conf import (
    NONE_SENTINEL,
    PENETRATION_TTL,
    jitter_ttl,
    DEFAULT_CACHE_TTL,
    CACHE_TTL_JITTER,
)

async def _clear():
   """隔离: 清掉所有博客缓存 key, 避免测试间串味。"""
   await invalidate_blog_list()
   await invalidate_blog_detail(123456)
   await invalidate_blog_detail(999999)

async def test_build_keys():
   assert build_list_key(None, None, 1, 10) == "blog:list:None:None:1:10"
   assert build_detail_key(7) == "blog:detail:7"

async def test_list_roundtrip():
   key = build_list_key(None, None, 1, 10)
   await _clear()
   # 未写: None
   assert await get_cached_blog_list(key) is None
   # 写入并读回
   payload = {"list": [{"id":1, "title": "t"}], "total": 1}
   await set_cached_blog_list(key, payload)
   got = await get_cached_blog_list(key)
   assert got == payload
   assert got ["total"] == 1
   # 失效后回归 None
   await invalidate_blog_list()
   assert await get_cached_blog_list(key) is None

async def test_list_serializes_nested():
   """set_cached_blog_list 内部 jsonable_encoder 能把嵌套结构序列化存回一致结构。"""
   key = build_list_key(2,"kw",3,10)
   await _clear()
   data = {"list":[{"id":5, "tags":["Python","AI"]}],"total":1}
   await set_cached_blog_list(key,data)
   got = await get_cached_blog_list(key)
   assert got["list"][0]["tags"] == ["Python","AI"]

async def test_detail_three_states():
   """详情缓存三态:MISS(None) -> ABSENT('NONE') -> HIT(真数据)"""
   bid= 123456
   await invalidate_blog_detail(bid)
   # MISS
   assert await get_cached_blog_detail(bid) is None
   # 写防穿透哨兵 -> ABSENT
   await set_blog_detail_none(bid)
   assert await get_cached_blog_detail(bid) == "NONE"
   # 写真实数据 -> HIT, 覆盖哨兵
   real = {"id":bid, "title":"hello"}
   await set_cached_blog_detail(bid,real)
   got = await get_cached_blog_detail(bid)
   assert got == real
   await invalidate_blog_detail(bid)

async def test_sentinel_is_dict_json_roundtrip():
   """哨兵必须是 dict, 保证json.loads 往返后 == 仍成立 (防穿透比较的基石)"""
   assert isinstance(NONE_SENTINEL, dict)
   import json
   back = json.loads(json.dumps(NONE_SENTINEL))
   assert back == NONE_SENTINEL

async def test_prefix_invalidation():
   """列表组合不可枚举, 统一按前缀清空。"""
   k1 = build_list_key(1,None, 1, 10)
   k2 = build_list_key(2,"x",2, 10)
   await set_cached_blog_list(k1,{"x":1})
   await set_cached_blog_list(k2, {"x": 2})
   await invalidate_blog_list()
   assert await get_cached_blog_list(k1) is None
   assert await get_cached_blog_list(k2) is None

async def test_jitter_ttl_range():
   """防雪崩:TTL 必须落在 [基础, 基础+抖动] 区间内。"""
   for _ in range(20):
      t = jitter_ttl()
      assert DEFAULT_CACHE_TTL <= t <= DEFAULT_CACHE_TTL + CACHE_TTL_JITTER