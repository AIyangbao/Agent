from fastapi import FastAPI
from pydantic import BaseModel,Field
import uvicorn

app = FastAPI()
#请求体
class Book(BaseModel):
    name:str=Field(...,min_length=2,max_length=20)
    author:str
    publisher:str=Field("黑马出版社")
    sell_price:int=Field(...,gt=0)

@app.post('/book/information')
async def get_book_information(book=Book):
    return {book}

# 注册: 用户名和密码 -> str
class User(BaseModel):
    username: str = Field(default="张三",min_length=2,max_length=10,description="用户名,长度限制为0~10")
    password: str = Field(min_length=3,max_length=20)

@app.post("/register")
async def register(user: User):
    return user

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)
