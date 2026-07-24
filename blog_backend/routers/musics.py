from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from curd.musics import get_music_list
from utils.response import success_response

router = APIRouter(prefix="/api/music", tags=["music"])

@router.get("/list")
async def list_music(db: AsyncSession = Depends(get_db)):
    rows = await get_music_list(db)
    return success_response(message="获取音乐列表成功",data=rows)