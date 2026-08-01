from fastapi import APIRouter, Depends, Query, HTTPException,Response, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
import html
from datetime import datetime
from curd.blogs import (
    get_blog_list,
    get_list_count,
    get_blog_detail,
)
from services.blog_rag import (
    create_blog_with_rag,
    update_blog_with_rag,
    delete_blog_with_rag,
)
from services.blog_cache import (
    build_list_key,
    get_cached_blog_list,
    set_cached_blog_list,
    get_cached_blog_detail,
    set_cached_blog_detail,
    set_blog_detail_none,
    invalidate_blog_list,
    invalidate_blog_detail,
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
    key = build_list_key(tagId,keyword, page, pageSize)
    cached = await get_cached_blog_list(key)
    if cached is not None:
        return success_response(message="获取博客列表成功(缓存)", data=cached)
    
    offset = (page - 1) * pageSize
    rows = await get_blog_list(db, tagId, offset, pageSize,keyword)
    total = await get_list_count(db, tagId,keyword)
    data = {"list": rows, "total": total}
    await set_cached_blog_list(key, data)
    return success_response(message="获取博客列表成功", data=data)


# 获取指定博客详情接口
@router.get("/detail")
async def detail_blog(id: int = Query(...), db: AsyncSession = Depends(get_db)):
    cached = await get_cached_blog_detail(id)
    if cached == "NONE":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="没有此文章信息")
    if cached is not None:
        return success_response(message="获取博客详情成功(缓存)",data=cached)
    blog = await get_blog_detail(db, id)
    if blog is None:
        await set_blog_detail_none(id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="没有此文章信息"
        )
    await set_cached_blog_detail(id,blog)
    return success_response(message="获取博客详情成功", data=blog)


# 添加博客接口
@router.post("/add")
async def add(
    blog: BlogCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await create_blog_with_rag(db, blog, current_user.id, background_tasks)
    await invalidate_blog_list()
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
    await delete_blog_with_rag(db, id)
    await invalidate_blog_list()
    await invalidate_blog_detail(id)
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
    result = await update_blog_with_rag(db, id, blog)
    await invalidate_blog_list()
    await invalidate_blog_detail(id)
    return success_response(message="修改博客成功", data=result)

# RSS 订阅源(公开, 无需登录)
@router.get('/rss')
async def blog_rss(
    limit: int = Query(20,le=50),
    db: AsyncSession = Depends(get_db),
):
    rows = await get_blog_list(db,None,0,limit)
    site = "https://blog.fireflyai.site"
    now = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0800")
    items = []
    for row in rows:
        b = row["Blog"]
        title = html.escape(b.title)
        link = f"{site}/posts/{b.id}"
        desc = html.escape((b.content or "")[:300])
        pub = (
            b.create_time.strftime("%a, %d %b %Y %H:%M:%S +0800")
            if b.create_time
            else now
        )
        items.append(
            f'    <item>\n'
            f'      <title>{title}</title>\n'
            f'      <link>{link}</link>\n'
            f'      <guid>{link}</guid>\n'
            f'      <pubDate>{pub}</pubDate>\n'
            f'      <description>{desc}</description>\n'
            f'    </item>'
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        '  <channel>\n'
        '    <title>技术宅小窝博客</title>\n'
        f'    <link>{site}</link>\n'
        '    <description>个人技术博客，记录学习与项目心得</description>\n'
        '    <language>zh-CN</language>\n'
        f'    <lastBuildDate>{now}</lastBuildDate>\n'
        f'{chr(10).join(items)}\n'
        '  </channel>\n'
        '</rss>'
    )
    return Response(content=xml, media_type="application/rss+xml")