"""
RAG 模块 · 第 4 层：检索 (Retrieve)
用户问题 -> embed -> 向量检索 -> 拼装成 LLM 可读的 context
"""
from .embeddings import embed_query
from .store import query
from utils.log import logger
import re
TOP_K = 3 # 找回几个最相似的块
STM_THRESHOLD = 0.85 # 余弦距离超过此值视为"不相关",直接丢弃

# --------- 检索门控 ---------
_MIN_LEN =2 # 空/单字基本是噪音, 不值得检索
# 常见客套话。注意用 ^...$ 整句匹配, 避免误伤"你好,帮我讲讲Docker"这种真问题
_CHITCHAT = re.compile(
    r"^(你好|您好|hi|hello|嗨|在吗|在不在|谢谢|谢啦|感谢|再见|拜拜|ok|okay|好的?|嗯+|哦+|哈哈+|"
    r"早|早上好|下午好|晚上好|晚安|测试|test)[!~。.,，！？\s]*$",
    re.IGNORECASE,
)
def should_retrieve(question: str) -> bool:
    """要不要为这个问题做一次向量检索。
    成本优化, 要【保守】: 宁可多检索(浪费一次embed), 也别漏掉真问题。"""
    q = (question or "").strip()
    if len(q) < _MIN_LEN: # 空/单字
        return False
    if _CHITCHAT.match(q): # 整句是客套话
        return False
    return True
def retrieve(user_question: str, top_k: int = TOP_K) -> dict:
    # 门控拦截: 明显闲聊直接返回"没检索到", 省掉一次 embedding 调用
    if not should_retrieve(user_question):
        logger.info(f"[RAG] 门控拦截(闲聊/噪音): {user_question!r}")
        return {"context":"","citations":[]}
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

    # 关键: 召回几条 / 距离分布 / 过阈值几条 —— 一眼看出检索质量
    logger.info(
        f"[RAG] 检索 q={user_question!r} 召回{len(dists)}条 "
        f"dist={[round(d, 3) for d in dists]} 过阈值{len(blocks)}条"
    )
    # 片段之间用空行分隔, 让LLM能区分不同来源
    context = "\n\n".join(blocks)
    return {"context": context, "citations": citations}