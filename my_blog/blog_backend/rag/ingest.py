"""
RAG 模块 · 第 3 层：入库流水线 (Ingest)
MySQL 文章 -> 切块 -> embed -> 存 Chroma
"""
from sqlalchemy import select

from config.db_conf import AsyncSessionLocal
from models.blogs import Blog
from .embeddings import embed_texts
from .store import add_chunks

CHUNK_SIZE = 500 # ，每块字符数(中文按字计)
CHUNK_OVERLAP = 50 # 块间重叠,避免切断语义边界
MIN_CONTENT_LEN = 50 # 正文最短长度,低于此视为噪声/测试文,不入库
def split_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """按长度切块,带重叠。返回chunk列表。"""
    text = (text or "").strip()
    if len(text) <= size:
        return [text] if text else []
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start += size - overlap
    return chunks

async def ingest_all():
    """全量入库: 拉所有未删除文章 -> 切块 -> embed -> 存Chroma"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Blog).where(Blog.is_delete == False)
        )
        posts = result.scalars().all()
    
    total = 0
    for post in posts:
        content = (post.content or "").strip()
        if len(content) < MIN_CONTENT_LEN: # 跳过测试文/灌水短文,不污染向量库
            continue
        chunks = split_text(post.content)
        if not chunks:
            continue
        embeddings = embed_texts(chunks) # 复用第1层
        metadatas = [{
            "post_id": post.id,
            "title": post.title,
            "link": f"https://blog.fireflyai.site/posts/{post.id}",
        } for _ in chunks]
        ids = [f"{post.id}_{i}" for i in range(len(chunks))] # 写入第2层
        add_chunks(chunks, embeddings,metadatas,ids)
        total += len(chunks)
    return total

async def ingest_one(post_id: int, title:str, content: str) -> int:
    """增量入库单篇。直接收数据,避免跨会话可见性竞争(请求事务未提交时另一会话读不到)。"""
    text = (content or "").strip()
    if len(text) < MIN_CONTENT_LEN:
       return 0 # 太短,不污染向量库   
    chunks = split_text(text)
    if not chunks:
        return 0
    embeddings = embed_texts(chunks)
    metadatas = [{
        "post_id": post_id,
        "title": title,
        "link": f"https://blog.fireflyai.site/posts/{post_id}",
    } for _ in chunks]
    ids = [f"{post_id}_{i}" for i in range(len(chunks))]
    add_chunks(chunks, embeddings, metadatas,ids) # store.py 里已用ipsert,同ID自覆盖
    return len(chunks)

def remove_one(post_id: int):
     """删除某篇文章的所有 chunk(软删除时调用)。Chroma 的 delete 按 metadata 过滤。"""
     from .store import get_collection
     col = get_collection()
     # 先查该文章有哪些ID,再精确删除
     res = col.get(where={"post_id":post_id},include=[])
     if res["ids"]:
         col.delete(ids=res["ids"])
     return len(res["ids"])