from fastapi import APIRouter, Depends, HTTPException
from config.db_conf import get_db
from schemas.users import UserRequest
from sqlalchemy.ext.asyncio import AsyncSession
from curd.users import get_user_by_name, create_user, login_user
from starlette import status
from utils.response import success_response
from utils.jwt import create_access_token
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
    login_result = await login_user(db, user_data)
    if login_result is None:
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
async def update_password():
    return
