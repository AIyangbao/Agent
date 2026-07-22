import os
from dashscope import TextEmbedding

os.environ["DASHSCOPE_API_KEY"] = "sk-933db338e50c42fd82ab226939d7b5b4"

resp = TextEmbedding.call(
    model="qwen3.7-text-embedding",
    input="博客 RAG 系统是什么？"
)

# ====== 新增诊断 ======
print("status_code:", getattr(resp, 'status_code', 'N/A'))
print("code:", getattr(resp, 'code', 'N/A'))
print("message:", getattr(resp, 'message', 'N/A'))
print("output type:", type(resp.output))
print("output:", resp.output)
# ====== 结束 ======

vec = resp.output["embeddings"][0]["embedding"]
print("维度:", len(vec))
print("前5维:", [round(x, 4) for x in vec[:5]])
print("模长(L2):", round(sum(x*x for x in vec) ** 0.5, 6))

