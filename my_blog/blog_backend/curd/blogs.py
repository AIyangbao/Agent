from sqlalchemy import select,update,func
from models.blogs import Blog
from models.tags import Blog_tags,tag
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.blogs import BlogCreate,BlogUpdate
from fastapi import HTTPException,Query
from typing import Optional
# 根据指定标签查询博客（含标签名，返回字典列表）
async def get_blog_list(db:AsyncSession,tag_id: Optional[int] = Query(None),skip:int=0,limit:int=10):
    if tag_id is None:
        query = select(Blog,tag.name).outerjoin(Blog_tags,Blog.id==Blog_tags.blog_id).outerjoin(tag,tag.id==Blog_tags.tag_id).where(Blog.is_delete==False).offset(skip).limit(10).order_by(Blog.create_time.desc())
    else:
        query = select(Blog,tag.name).join(Blog_tags,Blog.id == Blog_tags.blog_id).join(tag,tag.id==Blog_tags.tag_id).where(Blog_tags.tag_id == tag_id,Blog.is_delete==False).offset(skip).limit(limit).order_by(Blog.create_time.desc())
    result = await db.execute(query)
    blogs = result.mappings().all()
    return blogs

# 获取指定标签博客总量
async def get_list_count(db:AsyncSession,tag_id:Optional[int] = Query(None)):
    if tag_id is None:
        query = select(func.count(Blog.id)).where(Blog.is_delete==False)
    else:
        query = select(func.count(Blog.id)).join(Blog_tags,Blog.id == Blog_tags.blog_id).where(Blog_tags.tag_id == tag_id,Blog.is_delete==False)
    result = await db.execute(query)
    return result.scalar_one()

# 查询指定博客
async def get_blog_detail(db:AsyncSession,blog_id: int):
    query = select(Blog).where(Blog.id==blog_id,Blog.is_delete==False)
    result = await db.execute(query)
    blog = result.scalar_one_or_none()
    if not blog:
        return None
    tags_result = await db.execute(select(tag.name).join(Blog_tags,Blog_tags.tag_id == tag.id).where(Blog_tags.blog_id == blog_id))
    tag_names = [t[0] for t in tags_result.all()]
    return {"blog":blog,"tags":tag_names}

# 添加博客
async def add_blog(db:AsyncSession,blog_data: BlogCreate):
    blog = Blog(title=blog_data.title,content=blog_data.content,user_id=blog_data.user_id)
    db.add(blog)
    await db.flush()
    for tag_id in (blog_data.tag_ids or []):
     blog_tag = Blog_tags(blog_id=blog.id,tag_id=tag_id)
     db.add(blog_tag)
    return blog

# 删除博客
async def delete_blog(db:AsyncSession,blog_id: int):
    blog_data = await get_blog_detail(db,blog_id)
    if not blog_data or not blog_data["blog"]:
        raise HTTPException(status_code=404,detail="博客不存在")
    blog_data["blog"].is_delete = True
    return blog_data

# 修改博客
async def update_blog(db:AsyncSession,blog_id: int,blog_data:BlogUpdate):
    query = update(Blog).where(Blog.id == blog_id).values(**blog_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))
    result = await db.execute(query)

    # 检查更新
    if result.rowcount == 0:
        raise HTTPException(status_code=404,detail="博客不存在")
    
    # 获取一下更新后的博客
    updated_blog = await get_blog_detail(db,blog_id)
    return updated_blog

