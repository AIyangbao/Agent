from sqlalchemy import select
from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.users import UserRequest
from utils import security


# 根据用户名查询数据库
async def get_user_by_name(db: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    hashed_pwd = security.get_hash_password(user_data.password)
    user = User(User.username==user_data.username, password=hashed_pwd)
    db.add(user)
    await db.commit()
    return user
