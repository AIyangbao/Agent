from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

# 创建异步引擎
ASYNC_DATABASE_URL = "mysql+aiomysql://root:15358810yang@localhost:3306/news_app?charset=utf8mb4"
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False, # 输出SQL日志
    pool_size=5, # 设置连接池活跃的连接数
    max_overflow=10, # 允许额外的连接数
    pool_recycle =300, #定时强制回收闲置过久的数据库连接
    pool_pre_ping=True, # 取连接前探活
    pool_use_lifo=True # 优先复用新连接
)


#创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, # 绑定数据库引擎
    class_=AsyncSession, # 指定会话类
    expire_on_commit=False # 提交后会话不过期，不会重新查询数据库
)

# 依赖项 用于获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session # 返回数据库会话给路由处理函数
            await session.commit() # 提交事务
        except Exception:
            await session.rollback()
            raise

