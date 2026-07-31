from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from utils.response import success_response
from utils.auth import get_current_user
from models.users import User
from schemas.comments import CommentCreate, CommentResponse
from curd.comments import create_comment, get_comments_by_blog, delete_comment

router = APIRouter(prefix="/api/comments", tags=["comments"])

@router.get("/list")
async def list_comments(
    blogId: int = Query(..., description="博客ID"),
    db: AsyncSession = Depends(get_db),
):
    rows = await get_comments_by_blog(db, blogId)
    data = [
        CommentResponse(
            id=r["Comment"].id,
            blog_id=r["Comment"].blog_id,
            user_id=r["Comment"].user_id,
            username=r["username"],
            content=r["Comment"].content,
            parent_id=r["Comment"].parent_id,
            create_time=r["Comment"].create_time,
        )
        for r in rows
    ]
    return success_response(message="获取评论成功",data=data)

@router.post("/add")
async def add(
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await create_comment(db,comment, current_user.id)
    return success_response(message="评论成功")

@router.delete("/delete")
async def delete(
    id: int = Query(..., description="评论ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await delete_comment(db, id, current_user.id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    if result == "forbidden":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="你没有权限删除该评论")
    return success_response(message="删除评论成功")