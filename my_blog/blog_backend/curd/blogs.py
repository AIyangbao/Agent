from sqlalchemy import select,update,func
from models.blogs import Blog,Blog_tags
from sqlalchemy.ext.asyncio import AsyncSession
# 根据指定标签查询博客
async def get_tag_list(db:AsyncSession,tag: int,skip:int=0,limit:int=10):
    query = select(Blog).join(Blog_tags,Blog.id == Blog_tags.blog_id).where(Blog_tags.tag_id == tag).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

# 获取指定标签博客总量
async def get_list_count(db:AsyncSession,tag_id: int):
    query = select(func.count(Blog.id)).join(Blog_tags,Blog.id == Blog_tags.blog_id).where(Blog_tags.tag_id == tag_id)
    result = await db.execute(query)
    return result.scalar_one()

# 查询指定博客
async def get_blog_detail(db:AsyncSession,blog_id: int):
    query = select(Blog).where(Blog.id==blog_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


