from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get('/')
async def root_test():
    return {"message":"Hello World666"}

@app.get('/hello/{name}')
async def sat_hello_test(name:str):
    return {"message":f"hello {name}"}

@app.get('/')
async def root():
    return {"msg":"你好,FastAPI!"}

@app.get('/book/{id}')
async def get_book(id: int):
    return {"id":id,"title":f"这是第{id}本书"}


if __name__ == '__main__':
    uvicorn.run(app,host="127.0.0.1",port=8000)

