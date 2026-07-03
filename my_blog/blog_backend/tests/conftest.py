import os
import sys

#    环境变量必须在任何项目模块导入之前设置！
#    因为 config/settings.py 里 load_dotenv() + Settings() 是模块级代码，
#    它读到的是此时 os.environ 里的值。
#    如果漏了某个变量，Settings 对象初始化时 Pydantic 类型校验会崩。
#    setdefault() 只在变量不存在时才设值，不会覆盖你 .env 中的配置。
os.environ.setdefault("JWT_PWD","test_secret_key_for_testing_only")
os.environ.setdefault("DEBUG_MODE","true")
os.environ.setdefault("REDIS_HOST","localhost")
os.environ.setdefault("REDIS_PORT","6379")
os.environ.setdefault("REDIS_DB","0")

import pytest
import pytest_asyncio
from httpx import AsyncClient,ASGITransport
from sqlalchemy import text,event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,AsyncSession

from config.base import Base
from config.db_conf import get_db
from main import app

# 1. 创建测试用 SQLite 异步引擎
#    文件模式 "sqlite+aiosqlite:///./test.db" → 在项目根目录生成 test.db
#    优点：测试数据库不会在内存中消失，方便调试
#    想改纯内存测试的话，改成 "sqlite+aiosqlite:///:memory:"
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)



@event.listens_for(test_engine.sync_engine,"connect")
def enable_sqlite_fk(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 2. 覆盖真实 DB 依赖
#    FastAPI 的 app.dependency_overrides 机制：
#    所有路由里写的 Depends(get_db) → 现在都会走 override_get_db
async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

app.dependency_overrides[get_db] = override_get_db

# 3. 每个测试前重置数据库
#    autouse=True → 所有测试自动执行，不用手动调用
#    流程：删表 → 建表 → 插入 6 个默认标签
#    每个测试都是独立干净的数据库，互不影响
#
#    ⚠️ 为什么必须插入标签？
#    发文章会往 blog_tag 表插数据，blog_tag.blog_id 外键指向 blog，
#    blog_tag.tag_id 外键指向 tag。如果 tag 表是空的，外键约束直接失败。

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        # 6 个默认标签，和你项目 init_db.py 里的一致
        default_tags = ["Python","AI","Vue","Docker","FastAPI","其他"]
        for name in default_tags:
            await conn.execute(
                text("INSERT INTO tag(name,is_delete) VALUES(:name,0)"),
                {"name":name},
            )
    yield

# 4. 基础客户端（无登录态）
#    测试未鉴权场景：访问受保护接口应返回 401
@pytest_asyncio.fixture
async def client():
    """不携带任何token的纯客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as c:
        yield c

# 5. 已登录客户端 A
#    注册 → 拿到 token → 创建一个带着 token 的客户端
#    测试「自己的文章」的 CRUD 操作
@pytest_asyncio.fixture
async def auth_client_a(client):
    """注册用户 A,返回携带 A 的 token 的客户端"""
    resp = await client.post(
        "/api/user/register",
        json={"username":"user_a","password":"a123456"},
    )
    assert resp.status_code == 200,f"注册失败:{resp.text}"
    token = resp.json()["data"]["access_token"]

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization":f"Bearer {token}"},
    ) as c:
        yield c

@pytest_asyncio.fixture
async def auth_client_b(client):
    """注册用户B,返回携带B的token的客户端"""
    resp = await client.post(
        "/api/user/register",
        json={"username":"user_b","password":"b123456"},
    )
    assert resp.status_code == 200, f"注册失败: {resp.text}"
    token = resp.json()["data"]["access_token"]

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization":f"Bearer {token}"},
    ) as c:
         yield c
