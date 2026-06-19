from datetime import datetime, timedelta,timezone
import jwt
from fastapi import HTTPException,status
from config.settings import settings
# JWT配置
SECRET_KEY = settings.JWT_PWD
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 3 # token 3天过期

# 生成 token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode["exp"] = expire
    encode_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt

# 验证 token,取出里面的用户数据
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload #{"sub":user_id,"exp":...}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401,detail="Token 已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401,detail="Token无效")
