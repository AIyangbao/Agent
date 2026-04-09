from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends
from sqlalchemy import DateTime,func,Float,select,String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
import uvicorn


# 创建异步引擎
ASYNC_DATABASE_URL = "mysql+aiomysql://root:15358810yang@localhost:3306/FastAPI_first?charset=utf8mb4"
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True, # 输出SQL日志
    pool_size=10, # 设置连接池活跃的连接数
    max_overflow=20 # 允许额外的连接数
)

#  定义模型类: 基类 + 表对应的模型类
# 基类 创建时间、更新时间；书籍表：id、书名、作者、价格、出版社
class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime,default=func.now(),comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime,default=func.now(),onupdate=func.now(),comment="修改时间")

class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(primary_key=True,comment="书籍id")
    bookname: Mapped[str] = mapped_column(String(255),comment="书名")
    author: Mapped[str] = mapped_column(String(255),comment="作者")
    price: Mapped[float] = mapped_column(Float,comment="价格")
    publisher: Mapped[str] = mapped_column(String(255),comment="出版社")

# 建表: 定义函数建表 -> FastAPI 启动的时候调用建表的函数
async def create_tables():
    # 获取异步引擎,创建事务 - 建表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) #Base 模型类的元数据创建

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    await create_tables()
    yield
    # 关闭时执行
app = FastAPI(lifespan=lifespan)  

@app.get("/")
async def root():
    return {"message":"Hello World"}

if __name__ == "__main__":
 uvicorn.run(app,host="127.0.0.1",port=8000)