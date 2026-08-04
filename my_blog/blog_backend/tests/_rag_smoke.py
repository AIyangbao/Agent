"""
RAG 真链路冒烟测试（受控、最小额度消耗）
=======================================
只做一件事: 证明 embedding -> ChromaDB 入库 -> 检索命中 全链路通。
- 不跑 ingest_all（不会重刷全库、不乱吃额度）
- 塞一篇 post_id=99999 的测试短文, 检索语义相近问题, 断言命中
- 跑完用 remove_one 清理, 不污染真实向量库

运行:
    cd blog_backend
    ../venv/Scripts/python _rag_smoke.py   (或 ./venv/Scripts/python _rag_smoke.py)
"""
import os
import sys
import asyncio

# 1. 显式加载父目录 .env（settings 从 cwd 找 .env, 但真实 .env 在父目录）
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# RAG 链路不碰 DB, 但 config.settings 在 import 时强制解析 DB_*。
# 给一组 dummy 值仅为了让 settings 能初始化（不会被 RAG 路径用到）。
for k, v in {
    "DB_HOST": "127.0.0.1", "DB_PORT": "3306", "DB_USER": "rag_test",
    "DB_PWD": "rag_test", "DB_NAME": "rag_test",
}.items():
    os.environ.setdefault(k, v)

sys.path.insert(0, os.path.dirname(__file__))

# 2. 再次导入 settings 以拿到刚加载的 key
from config.settings import settings
if not settings.DASHSCOPE_API_KEY:
    print("❌ DASHSCOPE_API_KEY 未配置, 无法跑真实 embedding。请在 .env 中设置。")
    sys.exit(2)

from rag.ingest import ingest_one, remove_one
from rag.retrieve import retrieve

# 3. 一篇语义独特、不会和库里其他文章撞车的测试文
TEST_ID = 99999
TEST_TITLE = "玻色子采样与光量子计算前沿综述"
TEST_CONTENT = (
    "玻色子采样是一种专用的量子计算模型，利用压缩态光源和分束器网络产生不可经典模拟的输出分布。"
    "光量子计算路线以线性光学为基础，通过可编程干涉仪实现对单光子的高保真操控。"
    "九章系列光量子计算机在高斯玻色子采样任务上展示了远超经典超算的采样速率，"
    "证明了特定问题上量子优越性的可实现性。该路线的主要挑战在于光子损耗与探测效率。"
)
TEST_QUERY = "光量子计算是怎么利用玻色子采样实现量子优越性的？"


async def main():
    print(f"→ 入库测试文 (post_id={TEST_ID}, 标题={TEST_TITLE})")
    n = await ingest_one(TEST_ID, TEST_TITLE, TEST_CONTENT)
    print(f"  写入 chunk 数: {n}")
    if n == 0:
        print("❌ ingest_one 返回 0（正文过短被跳过），测试无法继续")
        return False

    print(f"→ 检索: {TEST_QUERY}")
    res = retrieve(TEST_QUERY)
    citations = res.get("citations", [])
    print(f"  命中引用数: {len(citations)}")
    for c in citations:
        print(f"    距离={c['distance']} | {c['title']}")

    # 断言: 至少命中一条, 且命中了我们刚写入的测试文
    hit = any(c["title"] == TEST_TITLE for c in citations)
    if not hit:
        print("❌ 检索未命中刚写入的测试文 —— RAG 链路疑似失效")
        return False

    dist = next(c["distance"] for c in citations if c["title"] == TEST_TITLE)
    print(f"✅ 命中测试文, 余弦距离={dist}（<0.85 阈值即通过相关性过滤）")
    return True


if __name__ == "__main__":
    try:
        ok = asyncio.run(main())
    finally:
        # 无论如何都清理测试数据, 不污染真实向量库
        try:
            removed = remove_one(TEST_ID)
            print(f"🧹 已清理测试 chunk 数: {removed}")
        except Exception as e:
            print(f"⚠️ 清理失败(可手动删 chroma_data 中 post_id={TEST_ID}): {e}")
    sys.exit(0 if ok else 1)
