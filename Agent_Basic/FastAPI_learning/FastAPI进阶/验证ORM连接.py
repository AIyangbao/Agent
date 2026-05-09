import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

# 替换成你的连接信息
ASYNC_DATABASE_URL = "mysql+aiomysql://root:15358810yang@localhost:3306/demo?charset=utf8mb4"

async def test_conn():
    engine = create_async_engine(ASYNC_DATABASE_URL)
    async with engine.connect() as conn:
        print("连接成功啦喵～")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_conn())