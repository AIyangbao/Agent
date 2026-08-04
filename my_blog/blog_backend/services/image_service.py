"""图片上传业务层 —— 纯函数，不依赖 FastAPI Request / 数据库。
负责校验图片类型与大小、生成存储路径、落盘，返回可访问的相对 URL。
"""
import os
import uuid
from datetime import datetime

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
ALLOWED_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg")
MAX_SIZE = 10 * 1024 * 1024

def save_image(data: bytes, filename: str, content_type: str) -> str:
    """保存图片，成功返回相对 URL,失败抛 ValueError(由路由层转成错误响应)。"""
    if not content_type or not content_type.startswith("image/"):
        raise ValueError("仅支持图片文件")
    if len(data) > MAX_SIZE:
        raise ValueError("图片不能超过10MB")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        ext = ".png"

    day = datetime.now().strftime("%Y%m%d")
    save_dir = os.path.join(UPLOAD_DIR, day)
    os.makedirs(save_dir, exist_ok=True)
    fname = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(save_dir, fname), "wb") as f:
        f.write(data)

    return f"/api/blogs/uploads/{day}/{fname}"