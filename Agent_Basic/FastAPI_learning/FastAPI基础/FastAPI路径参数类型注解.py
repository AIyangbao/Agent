from fastapi import FastAPI,Path
import uvicorn
app = FastAPI()

@app.get('/new/{id}')
async def get_new_id(id:int = Path(...,gt=0,lt=101,description="新闻id,取值范围1-100")):
    return {"new_id":f"新闻编号:{id}"}

@app.get('/new/{name}')
async def get_new_name(name:str = Path(...,min_length=2,max_length=10,description="新闻分类名称,取长范围2-10")):
    return {"new_name":f"新闻分类名{name}"}

if __name__ == '__main__':
    uvicorn.run(app,host='127.0.0.1',port=5600)
    

