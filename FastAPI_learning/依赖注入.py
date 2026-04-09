from fastapi import FastAPI,Query,Depends 
import uvicorn
app = FastAPI()

@app.get("/")
async def root():
    return {"message":"Hello World"}

# 分页参数逻辑共用: 新闻列表和用户列表
async def common_parameters(
        skip: int = Query(0,ge=0),
        limit: int = Query(10,le=60)
):
    return {"skip":skip,"limit":limit}

# 声明依赖项 -> 依赖注入
@app.get("/news/news_list")
async def get_news_list(commons=Depends(common_parameters)):
    return commons


@app.get("/user/user_list")
async def get_user_list(commons=Depends(common_parameters)):
    return commons

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)