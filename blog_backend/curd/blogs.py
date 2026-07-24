from sqlalchemy import select, update, func
from models.blogs import Blog
from models.tags import Blog_tags, tag
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.blogs import BlogCreate, BlogUpdate, BlogResponse
from typing import Optional


# 根据指定标签查询博客（含标签名，返回字典列表）
async def get_blog_list(
    db: AsyncSession, tag_id: Optional[int] = None, skip: int = 0, limit: int = 10,keyword: Optional[str] = None,
):
    query = (
            select(Blog, tag.name)
            .outerjoin(Blog_tags, Blog.id == Blog_tags.blog_id)
            .outerjoin(tag, tag.id == Blog_tags.tag_id)
            .where(Blog.is_delete == False)
        )
    if tag_id is not None:
        query = query.where(Blog_tags.tag_id == tag_id)
    if keyword:
        kw = f"%{keyword}%"
        query = query.where(
            Blog.title.like(kw) | Blog.content.like(kw)
        )
    query = query.offset(skip).limit(limit).order_by(Blog.create_time.desc())
    result = await db.execute(query)
    blogs = result.mappings().all()
    return blogs


# 获取指定标签博客总量
async def get_list_count(db: AsyncSession, tag_id: Optional[int] = None,keyword: Optional[str] = None):
    query = select(func.count(Blog.id)).where(Blog.is_delete == False)
    if tag_id is not None:
        query = query.join(Blog_tags, Blog.id == Blog_tags.blog_id).where(
            Blog_tags.tag_id == tag_id, Blog.is_delete == False)
    if keyword:
        kw = f"%{keyword}%"
        query = query.where(
            Blog.title.like(kw) | Blog.content.like(kw)
        )
    result = await db.execute(query)
    return result.scalar_one()


# 查询指定博客
async def get_blog_detail(db: AsyncSession, blog_id: int):
    query = select(Blog).where(Blog.id == blog_id, Blog.is_delete == False)
    result = await db.execute(query)
    blog = result.scalar_one_or_none()
    if not blog:
        return None
    tags_result = await db.execute(
        select(tag.name)
        .join(Blog_tags, Blog_tags.tag_id == tag.id)
        .where(Blog_tags.blog_id == blog_id)
    )
    tag_names = [row.name for row in tags_result.all()]
    result = BlogResponse(
        id=blog.id,
        title=blog.title,
        content=blog.content,
        user_id=blog.user_id,
        tags_name=tag_names,
    )
    return result


# 添加博客
async def add_blog(db: AsyncSession, blog_data: BlogCreate, user_id: int):
    blog = Blog(title=blog_data.title, content=blog_data.content, user_id=user_id)
    db.add(blog)
    await db.flush()
    for tag_id in blog_data.tag_ids or []:
        blog_tag = Blog_tags(blog_id=blog.id, tag_id=tag_id)
        db.add(blog_tag)
    await db.flush()
    return blog


# 删除博客
async def delete_blog(db: AsyncSession, blog_id: int):
    query = select(Blog).where(Blog.id == blog_id, Blog.is_delete == False)
    blog_data = await db.execute(query)
    result = blog_data.scalar_one_or_none()
    if not result:
        return None
    result.is_delete = True
    await db.flush()
    return result


# 修改博客
async def update_blog(db: AsyncSession, blog_id: int, blog_data: BlogUpdate):
    query = (
        update(Blog)
        .where(Blog.id == blog_id)
        .values(**blog_data.model_dump(exclude_unset=True, exclude_none=True))
    )
    result = await db.execute(query)
    # 检查更新
    if result.rowcount == 0:
        return None
    # 获取一下更新后的博客
    updated_blog = await get_blog_detail(db, blog_id)
    return updated_blog
