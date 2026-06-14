from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from curd.blogs import get_tag_list, get_list_count, get_blog_detail
from utils.response import success_response
from starlette import status

router = APIRouter(prefix="/api/blogs", tags=["blogs"])

#获取指定标签博客列表接口
@router.get("/list_blogs")
async def list_blogs(
    tagId: int = Query(...),
    page: int = 1,
    pageSize: int = Query(10, le=100),
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * pageSize
    rows = await get_tag_list(db, tagId, offset, pageSize)
    total = await get_list_count(db, tagId)
    return success_response(
        message="获取博客列表成功",
        data={"list": rows, "total": total}
    )

#获取指定博客详情接口
@router.get("/detail")
async def detail_blog(
    id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    blog = await get_blog_detail(db, id)
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="博客不存在")
    return success_response(
        message="获取博客详情成功",
        data=blog
    )

@router.post("/add")
async def add_blog(
    blog: 
    db: AsyncSession = Depends(get_db)
):