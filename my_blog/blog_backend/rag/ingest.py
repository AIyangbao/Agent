"""
RAG 模块 · 第 3 层：入库流水线 (Ingest)
MySQL 文章 -> 切块 -> embed -> 存 Chroma
"""
from sqlalchemy import select

from config.db_conf import AsyncSessionLocal
from models.blogs import Blog
from .embeddings import embed_texts
from .store import add_chunks
import asyncio
import re
CHUNK_SIZE = 500 # ，每块字符数(中文按字计)
CHUNK_OVERLAP = 50 # 块间重叠,避免切断语义边界
MIN_CONTENT_LEN = 50 # 正文最短长度,低于此视为噪声/测试文,不入库
def split_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """结构感知切块: 优先按段落(空行)边界切, 超长段落再按长度兜底。
    避免把句子/代码块拦腰砍断, 让每块语义完整。"""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]

    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, cur = [], ""
    for p in paragraphs:
        if len(p) > size: # 单段就超长 -> 按长度硬切(兜底, 保持重叠)
            if cur:
                chunks.append(cur); cur = ""  
            start = 0
            while start < len(p):
              end = start + size
              chunks.append(p[start:end])
              if end >= len(p):
                 break
              start += size - overlap
            continue
        if cur and len(cur) + len(p) + 2 > size: # 累加会超 size -> 封块, 开新块
            chunks.append(cur)
            cur = p
        else:
            cur = (cur + "\n\n" + p) if cur else p
    if cur:
        chunks.append(cur)        
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
    embeddings = await asyncio.to_thread(embed_texts,chunks)
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