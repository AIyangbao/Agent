from sqlalchemy import select, update, delete,func
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
    rows = result.mappings().all()

    # 多对多聚合: 一篇博客多个标签 -> 多行, 合并成 tags_name
    agg = {}
    for row  in rows:
        blog = row["Blog"]
        if blog.id not in agg:
            agg[blog.id] = BlogResponse(
                id = blog.id, title = blog.title, content = blog.content,
                user_id = blog.user_id, create_time = blog.create_time,tags_name = [],
            )
        if row["name"]:
            agg[blog.id].tags_name.append(row["name"])
    return list(agg.values())


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
        create_time=blog.create_time,
    )
    return result


# 添加博客
async def add_blog(db: AsyncSession, blog_data: BlogCreate, user_id: int):
    blog = Blog(title=blog_data.title, content=blog_data.content, user_id=user_id)
    db.add(blog)
    await db.flush()
    final_tag_ids = await _resolve_tag_ids(db, tag_ids=blog_data.tag_ids, tag_names=blog_data.tag_names)

    for tid in final_tag_ids:
        db.add(Blog_tags(blog_id=blog.id,tag_id=tid))
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

# 标签解析：存在则取 id，不存在则新建（add_blog / update_blog 共用）
async def _resolve_tag_ids(db: AsyncSession, tag_ids=None, tag_names=None) -> set[int]:
    final_tag_ids = set()
    if tag_ids:
        res = await db.execute(
            select(tag.id).where(tag.id.in_(tag_ids), tag.is_delete == False)
        )
        final_tag_ids.update(r.id for r in res.all())

    if tag_names:
        for name in tag_names:
            name = (name or "").strip()
            if not name:
                continue
            res = await db.execute(
                select(tag).where(tag.name == name, tag.is_delete == False)
            )
            existing =  res.scalar_one_or_none()
            if existing:
                final_tag_ids.add(existing.id)
            else:
                new_tag = tag(name=name)
                db.add(new_tag)
                await db.flush()
                final_tag_ids.add(new_tag.id)
    return final_tag_ids

# 修改博客
async def update_blog(db: AsyncSession, blog_id: int, blog_data: BlogUpdate):
    data = blog_data.model_dump(exclude_unset=True, exclude_none=True)
    tag_ids = data.pop("tag_ids",None)
    tag_names = data.pop("tag_names", None)
    if data:
        result = await db.execute(update(Blog).where(Blog.id == blog_id, Blog.is_delete == False).values(**data))
        # 检查更新
        if result.rowcount == 0:
          return None

    if tag_ids is not None or tag_names is not None:
        # 解析标签，获取最终有效的标签ID集合
        final_tag_ids = await _resolve_tag_ids(db, tag_ids=tag_ids, tag_names=tag_names)
        await db.execute(delete(Blog_tags).where(Blog_tags.blog_id == blog_id))
        # 插新关联
        for tid in final_tag_ids:
            db.add(Blog_tags(blog_id=blog_id, tag_id=tid))
        await db.flush()
    # 获取一下更新后的博客
    updated_blog = await get_blog_detail(db, blog_id)
    return updated_blog



