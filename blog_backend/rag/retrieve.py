"""
RAG 模块 · 第 4 层：检索 (Retrieve)
用户问题 -> embed -> 向量检索 -> 拼装成 LLM 可读的 context
"""
from .embeddings import embed_query
from .store import query

TOP_K = 3 # 找回几个最相似的块
STM_THRESHOLD = 0.85 # 余弦距离超过此值视为"不相关",直接丢弃

def retrieve(user_question: str, top_k: int = TOP_K) -> dict:
    """
    检索与问题最相关的博客片段。
    返回:
        {
          "context":   "片段1\n\n片段2\n\n...",   # 喂给 LLM 的检索上下文
          "citations": [                            # 引用来源，前端可展示
              {"title": "...", "link": "...", "distance": 0.59},
          ]
        }
    """
    # 问题向量化 (复用第1层)
    vector = embed_query(user_question)
    
    #  向量检索（复用第2层）。res 是嵌套结构！
    #    res["documents"]  = [[块1, 块2, 块3]]   → 外层是"一次查询"，内层是"结果列表"
    #    res["metadatas"]  = [[meta1, meta2, ...]]
    #    res["distances"]  = [[0.59, 0.71, ...]]
    #    所以我们永远取 res[...][0] 拿掉最外层
    res = query(vector,top_k=top_k)
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]

    # 拼装:过滤不相关块 + 提取引用
    blocks = []
    citations = []
    for d,m,dist in zip(docs,metas,dists):
        if dist > STM_THRESHOLD: # 距离太大 = 语义不相关，丢
            continue
        blocks.append(d)
        citations.append({
            "title": m["title"],
            "link": m["link"],
            "distance": round(dist,4),
        })
    
    # 片段之间用空行分隔, 让LLM能区分不同来源
    context = "\n\n".join(blocks)
    return {"context": context, "citations": citations}