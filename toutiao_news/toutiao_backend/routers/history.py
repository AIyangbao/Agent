from fastapi import APIRouter,Query,Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config.db_conf import get_db
from utils.auth import get_current_user
from utils.response import success_response
from models.users import User
from schemas.history import HistoryAddRequest,HistoryNewsItemResponse,HistoryListResponse
from crud import history
router = APIRouter(prefix="/api/history",tags=["history"])

#添加新闻浏览历史
@router.post("/add")
async def add_history(
    data:HistoryAddRequest,
    user:User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await history.add_history(db,user.id,data.news_id)
    return success_response(message="添加浏览历史成功",data=result)

@router.get("/list")
async def get_history_list(page: int = Query(1,ge=1),
                           page_size: int = Query(10,ge=1,le=100,alias="pageSize"),
                           user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    """
    获取历史记录列表"""
    rows,total = await history.get_history_list(db,user.id,page,page_size)

    has_more = total > page*page_size

    history_list = [HistoryNewsItemResponse.model_validate({
        **news.__dict__,
        "view_time": view_time,
        "history_id": history_id
    })for news,view_time,history_id in rows]

    data = HistoryListResponse(list=history_list,total=total,hasMore=has_more)

    return success_response(data=data)

@router.delete("/delete/{history_id}")
async def delete_history(history_id: int,
                         user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    """
    删除历史记录
    """
    result = await history.delete_history(db,user.id,history_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="历史记录")
    return success_response(message="删除成功")

@router.delete("/clear")
async def clear_history(user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    """
    清空历史记录
    """
    result = await history.clear_history(db,user.id)
    return success_response(message="清空成功")
