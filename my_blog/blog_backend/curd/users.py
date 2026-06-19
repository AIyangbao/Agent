from sqlalchemy import select
from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.users import UserRequest
from utils.security import get_hash_password,verify_password

# 根据用户id查询用户
async def get_user_by_id(db:AsyncSession,id:int):
   query = select(User).where(User.id == id,User.is_delete==False)
   result = await db.execute(query)
   return result.scalar_one_or_none()
# 根据用户名查询数据库
async def get_user_by_name(db: AsyncSession, username: str):
    query = select(User).where(User.username == username,User.is_delete==False)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    hashed_pwd = get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_pwd)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# 登录用户
async def login_user(db: AsyncSession,user_data: UserRequest):
    user = await get_user_by_name(db,user_data.username)
    if not user:
       return None
    if verify_password(user_data.password,user.password) is False:
       return None
    return user
    

# 修改用户密码
async def update_user(db: AsyncSession,user:User,old_password:str,new_password:str):
 if not verify_password(old_password,user.password):
    return False
 hashed_new_pwd = get_hash_password(new_password)
 user.password = hashed_new_pwd
 db.add(user)
 await db.commit()
 await db.refresh(user)
 return True    