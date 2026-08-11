"""博客专属工具：回答 RAG 检索干不了的"元数据/列举"类问题。
RAG 擅长"语义搜内容", 但"有哪些标签""最近发了哪些"这类要查库聚合, 向量检索答不了。"""
from tools.base import BaseTool, ToolDefinition
from config.db_conf import AsyncSessionLocal
from curd.tags import get_tag_list
from curd.blogs import get_blog_list

class ListTagsTool(BaseTool):
    """列出博客所有标签"""

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="list_blog_tags",
            description="列出博客现有的所有标签/分类,当用户问“有哪些标签”“有哪些分类”时调用",
            parameters={"tpye": "object", "properties": {}}, # 无参数
        )

    async def execute(self, ** kwargs) -> str:
        async with AsyncSessionLocal() as db: # 自己开 session, 不依赖 FastAPI 请求
            tags = await get_tag_list(db)
        if not tags:
            return "该博客暂无任何标签"
        names = "、".join(t["name"] for t in tags)
        return f"博客现有{len(tags)} 个标签: {names}"

class RecentBlogsTool(BaseTool):
    """列出最近发布的博客"""

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="list_recent_blogs",
            description="列出最近发布的博客文章(按时间排序), 当用户问“最近发了哪些博客”“最新文章”时调用",
            parameters={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer","description": "返回几篇, 默认5", "default": 5},
                },
            },
        )

    async def execute(self, limit: int = 2, **kwargs) -> str:
        limit = max(1, min(int(limit), 3)) ## 兜底: 夹在 1~3, 防 LLM 传离谱的值
        async with AsyncSessionLocal() as db:
            blogs = await get_blog_list(db, limit=limit)  # curd 已按 create_time 倒序
        if not blogs:
            return "还没有发布任何博客"
        lines = []
        for i, b in enumerate(blogs, 1):
            date = b.create_time.strftime("%Y-%m-%d") if b.create_time else "未知日期"
            tags = f"[标签: {','.join(b.tags_name)}]" if b.tags_name else ""
            lines.append(f"{i}. 《{b.title}》(f{date}{tags})")
        return f"最近发布的{len(blogs)} 篇博客: \n" + "\n".join(lines)
