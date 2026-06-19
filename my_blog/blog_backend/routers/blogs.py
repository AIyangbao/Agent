from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from curd.blogs import get_blog_list, get_list_count, get_blog_detail,add_blog,delete_blog,update_blog
from utils.response import success_response
from utils.auth import get_current_user
from starlette import status
from schemas.blogs import BlogCreate,BlogResponse,BlogUpdate
from models.users import User
from typing import Optional
router = APIRouter(prefix="/api/blogs", tags=["blogs"])

#获取指定标签博客列表接口
@router.get("/list_blogs")
async def list_blogs(
    tagId: Optional[int] = Query(None),
    page: int = 1,
    pageSize: int = Query(10, le=100),
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * pageSize
    rows = await get_blog_list(db, tagId, offset, pageSize)
    total = await get_list_count(db, tagId)
    data = {"list":rows,"total":total}
    return success_response(
        message="获取博客列表成功",
        data=data
    )

#获取指定博客详情接口
@router.get("/detail")
async def detail_blog(
    id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    blog = await get_blog_detail(db, id)
    return success_response(
        message="获取博客详情成功",
        data=blog
    )

#添加博客接口
@router.post("/add")
async def add(
    blog: BlogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    blog.user_id = current_user.id
    blog = await add_blog(db,blog)
    return success_response(
        message="添加博客成功",
        data=blog
    )

#软删除博客接口
@router.delete("/delete")
async def delete(id:int = Query(...),db:AsyncSession = Depends(get_db)):
    await delete_blog(db,id)
    return success_response(
        message="删除博客成功"
    )

#修改博客接口
@router.put("/update")
async def update(id: int ,blog: BlogUpdate,db:AsyncSession = Depends(get_db)):
    result = await update_blog(db,id,blog)
    return success_response(
        message="修改博客成功",
        data=result
    )


