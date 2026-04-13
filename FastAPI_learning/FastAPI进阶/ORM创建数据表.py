from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy import DateTime,func,Float,select,String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
import uvicorn
import numpy as np
from pydantic import BaseModel

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

#路由中使用ORM
# 需求: 查询功能的接口，查询图书 —> 依赖注入: 创建依赖项获取数据库会话 + Depends注入路由处理函数
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, # 绑定数据库引擎
    class_=AsyncSession, # 指定会话类
    expire_on_commit=False # 提交后会话不过期，不会重新查询数据库
)

async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session # 返回数据库会话给理由处理函数
            await session.commit() # 提交事务
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close() # 关闭会话

@app.get("/book/books")
async def get_book_list1(db: AsyncSession = Depends(get_database)):
    # 查询
    result = await db.execute(select(Book)) # 查询 ——> 返回一个ORM 对象
    #book = result.scalars().all() # 获取所有
    #book = result.scalars().first() # 获取第一个
    #book = await db.get(Book,5) # 获取单条数据 -> 根据主键
    book = result.scalar_one_or_none()
    return book


@app.get("/book/search_book")
async def get_search_book(db: AsyncSession = Depends(get_database)):
    # 需求 ： 条件 价格大于等于200
    #result = await db.execute(select(Book).where(Book.price >=200))
    #books = result.scalars().all()
    #return books(
    # 需求: 作者 以曾 开头 %_
    # like() 模糊查询: % 任意个字符：_一个单个字符
    result1 = await db.execute(select(Book).where((Book.author.like("曹_"))))

    #& | ~ 与非
    result2 = await db.execute(select(Book).where((Book.author.like("曹%")) | (Book.price>100)))
    # in_() 包含
    # 需求: 书籍id列表，数据库里面的id如果在书籍id列表里面就返回
    id_list=[1,3,5,7]
    result3 = await db.execute(select(Book).where(Book.id.in_(id_list)))
    book = result3.scalars().all()
    return book

@app.get("/book/count")
async def get_count(db: AsyncSession = Depends(get_database)):
    # 聚合查询 select( func.方法名(模型类.属性))
    result1 = await db.execute(select(func.count(Book.id)))
    result2 = await db.execute(select(func.max(Book.price)))
    result3 = await db.execute(select(func.avg(Book.price)))
    num = result3.scalar()
    return num

@app.get("/book/get_book_list")
async def get_book_list(
    page: int = 1,
    page_size: int =3,
    db: AsyncSession = Depends(get_database)
):
    # (页码 - 1) * page_size
    skip = (page - 1) * page_size
    # offset 跳过的记录数 : limit 每页的记录数
    stmt = select(Book).offset(skip).limit(page_size)
    result = await db.execute(stmt)
    books = result.scalars().all()
    return books

# 需求: 用户输入图书信息(id,书名、作者、价格、出版社) -> 新增
# 用户输入 -> 参数 -> 请求体
class BookBase(BaseModel):
    id: int
    bookname: str
    author: str
    price: float
    publisher: str

@app.post("/book/add_book")
async def add_book(book: BookBase, db: AsyncSession = Depends(get_database)):
    # ORM对象 -> add -> commit
    book_obj = Book(**book.__dict__)
    db.add(book_obj)
    await db.commit()
    return book

# 需求: 修改图书信息: 先查再改
# 设计思路: 路径参数书籍id: 作用是查找; 请求体参数: 作用是新数据(书名、作者、价格、出版社)
class BookUpdate(BaseModel):
    bookname: str
    author: str
    price: float
    publisher: str

@app.put("/book/update_book/{book_id}")
async def update_book(book_id: int, data: BookUpdate,db: AsyncSession = Depends(get_database)):
    # 1. 查找图书
    db_book = await db.get(Book,book_id)

    # 如果 未找到 抛出异常
    if db_book is None:
        raise HTTPException(
            status_code=404,
            detail="查无此书"
        )
    # 2. 找到了则修改: 重新赋值
    db_book.bookname = data.bookname
    db_book.author = data.author
    db_book.price = data.price
    db_book.publisher = data.publisher

    # 3. 提交到数据库
    await db.commit()
    return db_book



if __name__ == "__main__":
 uvicorn.run(app,host="127.0.0.1",port=8000)