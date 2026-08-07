from fastapi import APIRouter, Depends, HTTPException
from config.db_conf import get_db
from schemas.users import UserRequest, UserChangePasswordRequest, UserProfileUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from curd.users import get_user_by_name, create_user, login_user, update_user_password, get_user_by_id, update_user_profile
from services.ratelimit_service import is_locked, record_fail
from starlette import status
from models.users import User
from utils.response import success_response,error_response
from utils.jwt import create_access_token
from utils.auth import get_current_user
from datetime import timedelta

router = APIRouter(prefix="/api/user", tags=["users"])


# 用户注册接口
@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 注册逻辑: 先检验用户是否存在 -> 创建用户 -> 响应结果
    existing_user = await get_user_by_name(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在"
        )
    user = await create_user(db, user_data)
    # 注册成功直接生成token
    access_token = create_access_token(data={"sub": str(user.id)})
    return success_response(
        "用户注册成功", data={"access_token": access_token, "username": user.username}
    )


# 用户登录接口
@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 爆破防护: 该账号被锁直接拒
    if await is_locked(f"pwd:{user_data.username}"):
        raise HTTPException(status_code=429, detail="尝试次数过多, 请10分钟后再试")
    login_result = await login_user(db, user_data)
    if login_result is None:
        await record_fail(f"pwd:{user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户或密码错误"
        )
    # 生成token,把用户ID写进payload的“sub"字段
    access_token = create_access_token(
        data={"sub": str(login_result.id)}, expires_delta=timedelta(days=3)
    )
    return success_response("用户登录成功", data={"access_token": access_token})


# 用户修改接口
@router.put("/password")
async def update_password(data: UserChangePasswordRequest, 
                          db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user),
                          ):
    if not await update_user_password(db,current_user.id,data):
        return error_response(400, "原密码错误")
    return success_response("密码修改成功")

# 获取当前用户资料接口
@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return success_response("ok",data={
        "id": current_user.id,
        "username": current_user.username,
        "nickname": current_user.nickname,
        "avatar": current_user.avatar,
        "bio": current_user.bio,
        "phone": current_user.phone,
    })

# 更新资料 (昵称/头像/简介)
@router.put("/profile")
async def update_profile(
    data: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ok = await update_user_profile(db, current_user.id, data)
    if not ok:
        return error_response(400, "更新失败")
    return success_response("资料更新成功")