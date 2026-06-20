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
from sqlalchemy import text
from config.base import Base
from config.db_conf import async_engine
from models.users import User
from models.blogs import Blog
from models.tags import Blog_tags,tag

async def init_database():
    "初始化数据表,仅创建不存在的表，并插入初始标签数据"
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all,
                            checkfirst=True,
                            tables=Base.metadata.sorted_tables)
        print("所有数据表创建完成！")
        # 插入初始标签（幂等，重复执行不报错）
        await conn.execute(
            text("INSERT IGNORE INTO tag (id, name) VALUES "
                 "(1,'Python'),(2,'AI'),(3,'Vue'),(4,'FastAPI'),(5,'Docker'),(6,'其他')")
        )
        print("初始标签数据已就绪！")

if __name__ == "__main__":
    asyncio.run(init_database())