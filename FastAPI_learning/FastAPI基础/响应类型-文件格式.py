from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
app = FastAPI()

@app.get("/")
async def root():
    return {"message":"Hello World"}

# 接口: 返回一张图片内容
@app.get("/file")
async def get_file():
    path ="1.jpeg"
    return FileResponse(path)

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)