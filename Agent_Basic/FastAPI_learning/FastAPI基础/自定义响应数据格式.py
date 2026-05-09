from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
app = FastAPI()

@app.get("/")
async def root():
    return {"message":"Hello World"}

# 需求: 新闻接口 -> 响应数据格式 id、title、content
class News(BaseModel):
    id:int
    title: str
    content: str

@app.get("/news/{id}",response_model=News)
async def get_news(id:int):
    return {
        "id": id,
        "title": f"这是第{id}本书",
        "content":"这是一本好书"
    }

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)