import logging
from config.settings import settings
from fastapi import APIRouter,Depends
from services.sms_service import save_code,save_cooldown,gen_code,get_code,get_cooldown,verify_and_phone,sms_is_locked,sms_record_fail
from utils.jwt import create_access_token
from config.db_conf import get_db
from schemas.sms import PhoneIn, CodeLoginIn
from utils.response import success_response, error_response
from sqlalchemy.ext.asyncio import AsyncSession
from curd.users import get_or_create_user_by_phone
router = APIRouter(prefix="/api/sms",tags=["sms"])
logger = logging.getLogger("sms")
@router.post("/send")
async def send(data: PhoneIn):
    if await get_cooldown(data.phone):
        return error_response(429, "60秒内只能发一次")
    code = gen_code()
    await save_code(data.phone, code)
    await save_cooldown(data.phone)
    if settings.SMS_MOCK:
        logger.info("[MOCK SMS] %s -> %s", data.phone, code)
    return success_response(message="验证码已发送")

@router.post("/login")
async def login(data: CodeLoginIn, db: AsyncSession = Depends(get_db)):
    if await sms_is_locked(data.phone):
        return error_response()
    #  验证码校验
    if not await verify_and_phone(data.phone, data.code):
        await sms_record_fail(data.phone)
        return error_response(400,"验证码错误 or 已过期")
    # 注册+登录一体（查不到就建）
    user = await get_or_create_user_by_phone(db, data.phone)
    #复用现有 JWT（和 /api/users/login 同款 token，前端无需改）
    token = create_access_token(data={"sub": str(user.id)})
    return success_response(message="登录成功", data={"access_token": token})