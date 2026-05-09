from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
app = FastAPI()

@app.get("/")
async def root():
    return {"message":"hello World"}

# 接口 -> 响应HTML 代码
@app.get("/html",response_class=HTMLResponse)
async def get_html():
    return "<h1>这是一级标题<h2>"

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)