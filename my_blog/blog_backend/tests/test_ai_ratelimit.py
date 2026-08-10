"""限流 ai_rate_limited 单元测试。
思路：用"内存假 Redis"替换真 Redis，测试确定性、不用起 Redis、CI 也能跑。"""
import pytest
import services.ratelimit_service as rl

# ---------- 两个"假 Redis" ----------
class FakeRedis:
    """最小内存版 Redis:只实现 ai_rate_limited 用到的 incr / expire 两个命令。"""
    def __init__(self):
        self.store = {} # {key: 计数值}
        self.expire_calls = [] # 记录 expire 被调了几次/参数, 用来验证"只在窗口第一次设过期"

    async def incr(self, key):
        self.store[key] = int(self.store.get(key,0)) +1
        return self.store[key]

    async def expire(self, key, seconds):
        self.expire_calls.append((key,seconds))

class BrokenRedis:
    """模拟 Redis 挂了:incr 直接抛异常。"""
    async def incr(self, key):
        raise ConnectionError("redis down")

    async def expire(self, key, seconds):
        return True

# ---------- fixture：把模块里的 redis_client 换成假的 ----------
@pytest.fixture
def fake_redis(monkeypatch):
    fake = FakeRedis()
     # monkeypatch.setattr(模块对象, "属性名", 新值)：临时替换, 测试结束自动还原
    monkeypatch.setattr(rl, "redis_client", fake)
    return fake

# ---------- 5 个用例 ----------
async def test_under_limit_allowed(fake_redis):
    """没打满：前 AI_RATE_LIMIT 次都放行(返回 False)。"""
    for _ in range(rl.AI_RATE_LIMIT):
        assert await rl.ai_rate_limited(user_id=1) is False

async def test_over_limit_blocked(fake_redis):
    """打满后再来：第 LIMIT+1 次应拒绝(返回 True)。"""
    for _ in range(rl.AI_RATE_LIMIT):
        await rl.ai_rate_limited(user_id=1)
    assert await rl.ai_rate_limited(user_id=1) is True

async def test_users_isolated(fake_redis):
     """不同用户走不同 key,互不影响。"""
     for _ in range(rl.AI_RATE_LIMIT):
         await rl.ai_rate_limited(user_id=1) # 用户1打满
     assert await rl.ai_rate_limited(user_id=2) is False # 用户2不受影响

async def test_expire_set_only_on_first(fake_redis):
    """固定窗口的关键:expire 只在窗口第一次自增时设一次。"""
    await rl.ai_rate_limited(user_id=1)
    await rl.ai_rate_limited(user_id=1)
    await rl.ai_rate_limited(user_id=1)
    assert fake_redis.expire_calls == [("rl:ai:1", rl.AI_RATE_WINDOW)]

async def test_redis_down_fails_open(monkeypatch):
    """Redis 异常时降级放行(返回 False)，不因为限流把服务搞挂。"""
    monkeypatch.setattr(rl, "redis_client", BrokenRedis())
    assert await rl.ai_rate_limited(user_id=1) is False