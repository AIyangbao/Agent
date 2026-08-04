"""RSS 订阅源生成 —— 纯转换层，不依赖 FastAPI Request / 数据库。
只负责把文章数据转成 RSS 2.0 XML 字符串。
"""
import re
from email.utils import format_datetime
from datetime import datetime, timezone, timedelta
from html import escape

_CN_TZ = timezone(timedelta(hours=8))


def to_plain_text(md: str, max_len: int = 200) -> str:
    """Markdown/HTML 正文 -> 纯文本摘要。先取纯文本再截断，避免切断 HTML 实体。"""
    if not md:
        return ""
    text = re.sub(r"<[^>]+>", " ", md)             # 去 HTML 标签
    text = re.sub(r"[#*`>_~$$$$$$!|]", "", text)  # 去 Markdown 标记
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len]


def format_rfc822(dt) -> str:
    """datetime -> RFC822 字符串（+0800),兼容 naive/aware。"""
    if dt is None:
        dt = datetime.now(_CN_TZ)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=_CN_TZ)
    return format_datetime(dt)


def build_rss(items: list[dict], base_url: str, title: str = "技术宅小窝") -> str:
    """把文章 dict 列表组装为 RSS 2.0 XML。

    item 字段: id, title, content, create_time, tags(list[str])
    """
    base = base_url.rstrip("/")
    now = format_rfc822(None)
    item_xml = []
    for it in items:
        summary = escape(to_plain_text(it.get("content", "")))
        full = escape(it.get("content", "") or "")
        pub = format_rfc822(it.get("create_time"))
        cats = "".join(
            f"      <category>{escape(t)}</category>\n"
            for t in (it.get("tags") or [])
        )
        item_xml.append(
            f"    <item>\n"
            f"      <title>{escape(it['title'])}</title>\n"
            f"      <link>{base}/posts/{it['id']}</link>\n"
            f'      <guid isPermaLink="true">{base}/posts/{it['id']}</guid>\n'
            f"      <pubDate>{pub}</pubDate>\n"
            f"      <description>{summary}</description>\n"
            f'      <content:encoded xmlns:content="http://purl.org/rss/1.0/modules/content/">{full}</content:encoded>\n'
            f"{cats}"
            f"    </item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" '
        'xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        f"    <title>{escape(title)}</title>\n"
        f"    <link>{base}</link>\n"
        "    <description>个人技术博客，记录学习与项目心得</description>\n"
        "    <language>zh-CN</language>\n"
        f"    <lastBuildDate>{now}</lastBuildDate>\n"
        f'    <atom:link href="{base}/api/blogs/rss" rel="self" type="application/rss+xml" />\n'
        f"{chr(10).join(item_xml)}\n"
        "  </channel>\n"
        "</rss>"
    )


def generate_blog_feed(rows, base_url: str) -> str:
    """ORM 行 -> RSS。集中处理属性名差异9tags_name 等），对路由透明。"""
    items = [
        {
            "id": getattr(b, "id", None),
            "title": getattr(b, "title", ""),
            "content": getattr(b, "content", "") or "",
            "create_time": getattr(b, "create_time", None),
            "tags": getattr(b, "tags_name", []) or [],
        }
        for b in rows
    ]
    return build_rss(items, base_url)
