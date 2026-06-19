from fastapi import Header,Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from starlette import status
from config.db_conf import get_db
from curd.users import get_user_by_id
from utils.jwt import verify_token

# HTTPBearer 会自动从请求头里取 Authorization: Bearer <token>
security = HTTPBearer()
# 根据token 查询用户,返回用户
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
):
    # 验证 token
    payload = verify_token(credentials.credentials)
    user_id = int(payload.get("sub"))
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="无效的令牌或令牌已经过期")
    user = await get_user_by_id(db,user_id)
    if not user:
        raise HTTPException(status_code=401,detail="用户不存在")
    return user
    