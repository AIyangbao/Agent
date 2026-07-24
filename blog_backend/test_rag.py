import asyncio, sys
sys.path.insert(0,".")
from rag.ingest import ingest_all
from rag.store import query
from rag.embeddings import embed_query

async def main():
    # 1. 入库
    n = await ingest_all()
    print(f"入库chunk数:{n}")

    # 查回
    q_vec = embed_query("如何搭建博客AI Agent?")
    res = query(q_vec,top_k=3)
    docs,metas,dists = res["documents"][0],res["metadatas"][0],res["distances"][0]
    print(f"\n相似top-3:")
    for d, m, dist in zip(docs,metas,dists):
        print(f" 距离={dist:4f} | <<{m['title']}>>")
        print(f"    片段:{d[:70].replace(chr(10),'')}...")
    from rag.retrieve import retrieve

    r = retrieve("如何搭建博客AI Agent?")
    print("\n=== RAG 检索到的 context（前500字）===")
    print(r["context"][:500])
    print("\n=== 引用来源 ===")
    for c in r["citations"]:
       print(f"  {c['title']}  (距离 {c['distance']})  -> {c['link']}")


asyncio.run(main())