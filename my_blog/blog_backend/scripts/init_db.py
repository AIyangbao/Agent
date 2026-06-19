import sys
from pathlib import Path

# 获取当前脚本文件路径
script_path = Path(__file__).resolve()
# blog_backend路径
backend_root = script_path.parent.parent
# my_blog路径
project_root =backend_root.parent
# 添加进Python搜索路径
sys.path.insert(0,str(backend_root))
sys.path.insert(0,str(project_root))


import asyncio
from config.base import Base
from config.db_conf import async_engine
from models.users import User
from models.blogs import Blog
from models.tags import Blog_tags,tag

async def init_database():
    "初始化数据表,仅创建不存在的表"
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all,
                            checkfirst=True,
                            tables=Base.metadata.sorted_tables)
        print("所有数据表初始化完成！")

if __name__ == "__main__":
    asyncio.run(init_database())