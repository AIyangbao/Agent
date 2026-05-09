from fastapi import FastAPI,Query
import uvicorn
from pydantic import BaseModel

app = FastAPI()

@app.get('/book/book_find')
async def get_book_type(type:str=Query('Python开发',min_length=5, max_length=255),
                        price:int=Query(...,gt=50,lt=101)):
    return{"type":f"查询图书类别{type}","price":f"图书价格{price}"}

if __name__ == '__main__':
    uvicorn.run(app,host="127.0.0.1",port=8000)