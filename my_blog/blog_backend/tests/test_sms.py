"""短信验证码模块测试。依赖 conftest 的 redis_isolated 自动覆盖 cache_conf.redis_client。"""
import pytest
from config.cache_conf import get_cache

VALID_PHONE = "13800138000"

class TestSmsSend:
    async def test_send_and_cooldown(self, client):
        r = await client.post(f"/api/sms/send", json={"phone": VALID_PHONE})
        assert r.status_code == 200
        # 60s 冷却内重复发 → 429
        r2 = await client.post("/api/sms/send", json={"phone": VALID_PHONE})
        assert r2.status_code == 429

    async def test_invalid_phone_rejected(self, client):
        r = await client.post("/api/sms/send", json={"phone": "123"})
        assert r.status_code == 422 # Pydantic 正则拦截

class TestSmsLogin:
    async def test_wrong_code(self, client):
        await client.post("/api/sms/send", json={"phone": VALID_PHONE})
        r = await client.post("/api/sms/login",
                              json={"phone": VALID_PHONE, "code": "000000"})
        assert r.status_code == 400

    async def test_login_success(self, client):
        await client.post("/api/sms/send", json={"phone": VALID_PHONE})
        code = await get_cache(f"sms:code:{VALID_PHONE}") #直接读redis拿码
        assert code
        r = await client.post("/api/sms/login",
                              json={"phone": VALID_PHONE, "code": code})
        assert r.status_code == 200
        assert r.json()["data"]["access_token"]