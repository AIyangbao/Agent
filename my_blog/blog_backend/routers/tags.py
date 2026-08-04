from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from models.tags import tag
from curd.tags import get_tag_list
from utils.response import success_response
router = APIRouter(prefix="/api/tags",tags=["tags"])

@router.get("/list")
async def list_tags(db: AsyncSession = Depends(get_db)):
    data = await get_tag_list(db)
    return success_response(data=data)
