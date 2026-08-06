from sqlalchemy import select
from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.users import UserRequest,UserChangePasswordRequest
from utils.security import get_hash_password, verify_password


# 根据用户id查询用户
async def get_user_by_id(db: AsyncSession, id: int):
    query = select(User).where(User.id == id, User.is_delete == False)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 根据用户名查询数据库
async def get_user_by_name(db: AsyncSession, username: str):
    query = select(User).where(User.username == username, User.is_delete == False)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    hashed_pwd = get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_pwd)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


# 登录用户
async def login_user(db: AsyncSession, user_data: UserRequest):
    user = await get_user_by_name(db, user_data.username)
    if not user:
        return None
    if not verify_password(user_data.password, user.password):
        return None
    return user


# 修改用户密码
async def update_user_password(
    db: AsyncSession, user_id: int, data: UserChangePasswordRequest
):
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    if not verify_password(data.old_password, user.password):
        return False
    user.password = get_hash_password(data.new_password)
    await db.flush()
    return True
# 根据手机号查询用户
async def get_or_create_user_by_phone(db: AsyncSession, phone: str):
    user = (await db.execute(select(User).where(User.phone == phone, User.is_delete == False))).scalar_one_or_none()
    if user:
        return user
    import secrets
    user = User(
        username=f"u_{phone}",
        password=get_hash_password(secrets.token_hex(8)), # 验证码登录无密码, 给随机占位
        phone=phone,
    )
    db.add(user)
    await db.flush()
    await db.commit()
    await db.refresh(user)
    return user
