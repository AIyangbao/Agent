from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from curd.blogs import (
    get_blog_list,
    get_list_count,
    get_blog_detail,
    add_blog,
    delete_blog,
    update_blog,
)
from utils.response import success_response
from utils.auth import get_current_user
from starlette import status
from schemas.blogs import BlogCreate, BlogUpdate
from models.users import User
from typing import Optional

router = APIRouter(prefix="/api/blogs", tags=["blogs"])


# 获取指定标签博客列表接口
@router.get("/list_blogs")
async def list_blogs(
    tagId: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None,description="搜索关键词"),
    page: int = 1,
    pageSize: int = Query(10, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * pageSize
    rows = await get_blog_list(db, tagId, offset, pageSize,keyword)
    total = await get_list_count(db, tagId,keyword)
    data = {"list": rows, "total": total}
    return success_response(message="获取博客列表成功", data=data)


# 获取指定博客详情接口
@router.get("/detail")
async def detail_blog(id: int = Query(...), db: AsyncSession = Depends(get_db)):
    blog = await get_blog_detail(db, id)
    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="没有此文章信息"
        )
    return success_response(message="获取博客详情成功", data=blog)


# 添加博客接口
@router.post("/add")
async def add(
    blog: BlogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    create_blog = await add_blog(db, blog, current_user.id)
    result = await get_blog_detail(db,create_blog.id)
    return success_response(message="添加博客成功", data=result)


# 软删除博客接口
@router.delete("/delete")
async def delete(
    id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    blog = await get_blog_detail(db, id)
    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="没有此文章信息"
        )
    if blog.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限删除此文章"
        )
    await delete_blog(db, id)
    return success_response(message="删除博客成功")


# 修改博客接口
@router.put("/update")
async def update(
    id: int,
    blog: BlogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog_data = await get_blog_detail(db, id)
    if blog_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="没有此文章信息"
        )
    if blog_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="你没有权限修改此文章"
        )
    result = await update_blog(db, id, blog)
    return success_response(message="修改博客成功", data=result)
