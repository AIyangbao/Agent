from rag.ingest import ingest_one, remove_one
from curd.blogs import add_blog,update_blog,get_blog_detail,delete_blog
async def _safe_ingest(post_id: int,title: str, content: str):
    """RAG 是增强功能,异常必须吞掉,绝不让它影响核心发文。"""
    try:
        n = await ingest_one(post_id, title, content)
        print(f"[RAG]文章{post_id}入库完成, chunk数={n}")
    except Exception as e:
         print(f"[RAG]文章{post_id}入库失败(不影响业务):{e}")

def _safe_remove(post_id: int):
    try:
        n = remove_one(post_id)
        print(f"[RAG]文章{post_id}已从向量库移除,chunk数={n}")
    except Exception as e:
        print(f"[RAG]文章 {post_id} 移除失败(不影响业务):{e}")

async def create_blog_with_rag(db,blog,user_id,background_tasks=None):
    """发文章: 写库 + 增量入向量库。RAG 失败不影响发文。"""
    post = await add_blog(db, blog, user_id)
    if background_tasks is not None:
        background_tasks.add_task(_safe_ingest, post.id, post.title, post.content)
    else:
        await _safe_ingest(post.id,post.title,post.content)
    return await get_blog_detail(db, post.id)

async def update_blog_with_rag(db,blog_id,blog):
    """改文章: 写库 + 重新入向量库(upsert 覆盖旧chunk)。"""
    result = await update_blog(db,blog_id,blog)
    existing = await get_blog_detail(db,blog_id)
    title = blog.title if blog.title is not None else (existing.title if existing else "")
    content = blog.content if blog.content is not None else (existing.content if existing else "")
    await _safe_ingest(blog_id, title, content)
    return result

async def delete_blog_with_rag(db, blog_id):
    """删文章: 写库 + 从向量库移除对应chunk."""
    await delete_blog(db,blog_id)
    _safe_remove(blog_id)