from fastapi import APIRouter, Depends, Query, HTTPException,Response, BackgroundTasks, Request, UploadFile, File
from fastapi.responses import Response
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
    get_blog_detail_with_mutex,
)
from services.redis_lock import RedisLockCtx
from services.rss_service import generate_blog_feed
from services.image_service import save_image
from services.uv_service import record_uv, count_uv
from utils.response import success_response, error_response
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
    data = {"list": [b.model_dump() for b in rows], "total": total}
    await set_cached_blog_list(key, data)
    return success_response(message="获取博客列表成功", data=data)


# 获取指定博客详情接口
@router.get("/detail")
async def detail_blog(id: int = Query(...), db: AsyncSession = Depends(get_db), request: Request = None):
    client_ip = request.client.host if request and request.client else "unknown"
    # 先查缓存: 命中直接返回(带"缓存"标记), 与列表路由保持一致
    cached = await get_cached_blog_detail(id)
    if cached == "NONE":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="没有此文章信息")
    if cached is not None:
        await record_uv(f"uv:blog:{id}", client_ip) # 注意: 命中缓存也要记 UV, 别丢
        await record_uv(f"uv:site:all", client_ip)
        return success_response(message="获取博客详情成功(缓存)",data=cached)
    # 未命中 -> 走互斥锁回源
    result = await get_blog_detail_with_mutex(id,db)
    if result == "NONE":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="没有此文章信息")
     #  记录独立访客（HyperLogLog 自动去重）
    await record_uv(f"uv:blog:{id}", client_ip)
    await record_uv("uv:site:all", client_ip)
    return success_response(message="获取博客详情成功", data=result)


# 添加博客接口
@router.post("/add")
async def add(
    blog: BlogCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 按用户加锁：防同一用户并发重复提交（前端连点 / 网络重试）
    async with RedisLockCtx(f"add_blog:{current_user.id}", expire=10) as lock:
        if lock is None: # 没拿到锁 = 别人正在发，直接拒
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="操作过于频繁, 请稍后再试",
            )
        result = await create_blog_with_rag(db, blog, current_user.id, background_tasks)
    # with 块结束 → 自动释放锁（取消看门狗 + Lua 删锁）
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
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    rows = await get_blog_list(db,None,0,limit)
    # 用请求 host 拼站点地址，本地/线上自动适应，不再硬编码域名
    base = str(request.base_url).rstrip("/") if request else "https://blog.fireflyai.site"
    xml = generate_blog_feed(rows, base)
    return Response(content=xml, media_type="application/rss+xml")

@router.get('/sitemap.xml')
async def sitemap(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    rows = await get_blog_list(db, None, 0, 1000)  # 取全部文章
    base = str(request.base_url).rstrip("/")       # 本地/线上自动适应，不再硬编码
    urls = [f"  <url><loc>{base}/</loc></url>"]
    for r in rows:
        bid = getattr(r, "id", None)               # BlogResponse 是模型对象，用属性访问
        if bid is None:
            continue
        urls.append(f"  <url><loc>{base}/posts/{bid}</loc></url>")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>"
    )
    return Response(content=xml, media_type="application/xml")

@router.post("/upload_image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    # 读文件 -> 调业务层 -> 返回响应
    try:
        data = await file.read()
        url = save_image(data, file.filename, file.content_type)
    except ValueError as e:
        return error_response(400, str(e))
    except Exception as e:
        return error_response(500, f"上传失败:{e}")
    return success_response(message="上传成功", data={"url": url})

@router.get("/uv")
async def blog_uv(id: int = Query(...), db: AsyncSession =Depends(get_db)):
    return success_response(data={"blog_uv": await count_uv(f"uv:blog:{id}")})
