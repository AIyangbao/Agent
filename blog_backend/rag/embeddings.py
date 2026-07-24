"""
RAG 模块 · 第 1 层：文本向量化 (Embedding)
=========================================
把"文章正文 / 用户提问"变成高维向量。
模型：阿里云百炼 qwen3.7-text-embedding
  - 1024 维
  - 输出已 L2 归一化 (模长=1)
  - 免费额度 100 万 token（控制台"向量模型"tab 可见）
"""
from dashscope import TextEmbedding

# 与百炼控制台"向量模型"里显示的模型名完全一致
EMBED_MODEL = "qwen3.7-text-embedding"
# dashscope 单次批量上线较保守,分批避免超时/限流
_BATCH_SIZE = 8

def embed_texts(texts):
    """
    批量文本 -> 向量列表
    :param texts: ["文章1", "文章2", ...]
    :return:      [[v1...], [v2...], ...]  每个向量 1024 维
    """
    if isinstance(texts,str):
       texts = [texts]
    
    vectors = []
    # 分批调用 (每批最多 _BATCH_SIZE 条)
    for i in range(0,len(texts), _BATCH_SIZE):
        batch = texts[i: i + _BATCH_SIZE]
        resp = TextEmbedding.call(model=EMBED_MODEL, input=batch)

        # 防御: 远程调用可能失败(网络/额度/限流)
        if resp.status_code != 200 or resp.output is None:
            raise RuntimeError(
                f"embedding 失败: code={resp.code},msg={resp.message}"
            )

        # resp.output["embeddings"] 按输入顺序返回的列表
        for item in resp.output["embeddings"] :
            vectors.append(item["embedding"])
    return vectors

def embed_query(text):
    """单条查询向量化(复用同一模型,保证与文档同语义空间)"""
    return embed_texts([text])[0]
