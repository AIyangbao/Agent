from fastapi import APIRouter,Depends,HTTPException
from config.db_conf import get_db
from schemas.users import UserRequest
from sqlalchemy.ext.asyncio import AsyncSession
from curd import users
from starlette import status
from utils import response
router = APIRouter(prefix="/api/user",tags=["users"])

#用户注册接口
@router.post("/register")
async def register(user_data:UserRequest,db:AsyncSession = Depends(get_db)):
     # 注册逻辑: 先检验用户是否存在 -> 创建用户 -> 响应结果
     existing_user = await users.get_user_name(db,user_data.username)
     if existing_user:
          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="用户已存在")
     user = users.create_user(db,user_data)
     return response.success_response("用户注册成功",user)

# 用户登录接口
@router.post("/login")
async def login(user_data:UserRequest,db:AsyncSession = Depends(get_db)):
     return

     
