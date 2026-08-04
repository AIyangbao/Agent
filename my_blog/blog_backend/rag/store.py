"""
RAG 模块 · 第 2 层：向量存储 (Chroma)
把 embed_texts() 产出的向量持久化到本地，并支持相似检索。
"""


PERSIST_DIR = "./chroma_data" # 本地持久化目录
COLLECTION = "blog_chunks" # 集合名

_client = None # 单例: 避免每次调用都重新把HNSW索引加载进内存

def get_client():
    import chromadb
    from .embeddings import embed_texts
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=PERSIST_DIR)
    return _client

def get_collection():
    client = get_client()
    # hnsw: space=cosine;向量已L2归一化,cosine排序等价于点积排序
    return client.get_or_create_collection(
        name=COLLECTION,
        metadata={"hnsw:space":"cosine"},
    )

def add_chunks(chunks, embeddings, metadatas,ids):
    """批量写入: 文本 + 向量 + 元数据 + 唯一主键"""
    col = get_collection()
    col.upsert(documents=chunks,embeddings=embeddings,
            metadatas=metadatas,ids=ids)

def query(vector, top_k=3):
    """查询向量 -> 最相似的top_k个chunk"""
    col = get_collection()
    return col.query(query_embeddings=[vector],n_results=top_k,
                     include=["documents","metadatas","distances"])

