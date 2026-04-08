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

@app.get('/book/information')
async def get_book_information(book=Book):
    return {book}

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)
