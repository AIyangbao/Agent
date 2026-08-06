"""短信验证码业务层：复用 config.cache_conf 的 redis 引擎与语义化缓存函数。
不自己 new 连接，避免连接数膨胀 + 失去测试隔离。
"""
import  secrets
from config.cache_conf import set_cache, get_cache, delete_cache
from services.ratelimit_service import is_locked,record_fail

CODE_TTL,COOLDOWN_TTL, FAIL_TTL = 300, 60, 600 # 验证码 5 分/冷却60秒/锁定10分
MAX_FAIL = 5

def gen_code() -> str:
     return f"{secrets.randbelow(1_000_000):06d}"

async def save_code(phone: str, code: str) -> None:
     # set_cache 内部就是 setex，且自带 try/except 兜底（redis 挂了也不 500）
     await set_cache(f"sms:code:{phone}", code, expire=CODE_TTL)

async def save_cooldown(phone: str) -> None:
     await set_cache(f"sms:cooldown:{phone}", "1", expire=COOLDOWN_TTL)

async def get_code(phone: str):
     return await get_cache(f"sms:code:{phone}")

async def get_cooldown(phone: str):
     return await get_cache(f"sms:cooldown:{phone}")

async def verify_and_phone(phone: str, code: str) -> bool:
     saved = await get_code(phone)
     if not saved or saved != code:
          return False
     await delete_cache(f"sms:code:{phone}") # 一次性, 防重做
     return True

async def sms_is_locked(phone):
     return await is_locked(f"sms:{phone}")

async def sms_record_fail(phone):
     return await record_fail(f"sms:{phone}")