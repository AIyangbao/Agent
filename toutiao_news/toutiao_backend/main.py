from fastapi import FastAPI
from routers import news
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# 允许的来源
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # 允许的源,开发阶段允许所有源，生产环境需要指定源
    allow_credentials=True, # 允许携带的cookie
    allow_methods=["*"],    # 允许的请求方法
    allow_headers=["*"],    # 允许的请求头
)
@app.get("/")
async def root():
    return {"message":"Hello World"}

# 挂载路由/注册路由
app.include_router(news.router)

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)