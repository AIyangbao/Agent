import uvicorn
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import musics,blogs, users,ai,comments,tags
from fastapi.middleware.cors import CORSMiddleware
from utils.exception_handlers import register_exception_handlers

# 实例化API
app = FastAPI()

# 注册异常处理器
register_exception_handlers(app)

# 全局跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源,开发阶段允许所有源,生产环境需要指定源
    allow_credentials=True,  # 允许携带的cookie
    allow_methods=["*"],  # 允许的请求方法
    allow_headers=["*"],  # 允许的请求头
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "ok"}


# 挂载路由/注册路由
app.include_router(blogs.router)
app.include_router(users.router)
app.include_router(ai.router)
app.include_router(musics.router)
app.include_router(comments.router)
app.include_router(tags.router)

# 挂载静态目录
_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(_UPLOAD_DIR, exist_ok=True)
app.mount("/api/blogs/uploads", StaticFiles(directory=_UPLOAD_DIR), name="uploads")
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
