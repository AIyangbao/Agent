from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

# 创建异步引擎
ASYNC_DATABASE_URL = "mysql+asyncmy://root:15358810yang@localhost:3306/news_app?charset=utf8mb4"
import os
# 区分环境：pytest运行时禁用连接池，生产用标准池
is_test = os.getenv("PYTEST_CURRENT_TEST") is not None

if is_test:
    # NullPool：每次会话全新连接，用完彻底销毁，无池复用就不会有句柄残留
    engine_kwargs = {"poolclass": None, "echo": False}
else:
    engine_kwargs = {
        "echo": False,
        "pool_size":5,
        "max_overflow":10,
        "pool_recycle":300,
        "pool_pre_ping":True,
        "pool_use_lifo":True
    }

async_engine = create_async_engine(ASYNC_DATABASE_URL,** engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
    # 完全删掉手动await session.close()，async with自动回收

