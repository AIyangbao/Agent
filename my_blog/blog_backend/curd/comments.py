from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.comments import Comment
from models.users import User
from schemas.comments import CommentCreate

async def create_comment(db: AsyncSession, data: CommentCreate, user_id: int):
    comment = Comment(
        blog_id=data.blog_id,
        content=data.content,
        user_id=user_id,
        parent_id=data.parent_id,
    )
    db.add(comment)
    await db.flush()
    await db.commit()
    return comment

async def get_comments_by_blog(db: AsyncSession, blog_id: int):
    query =( select(Comment, User.username)
    .join(User, Comment.user_id == User.id)
    .where(Comment.blog_id == blog_id, Comment.is_delete == False)
    .order_by(Comment.create_time.desc())
    )
    result = await db.execute(query)
    return result.mappings().all()

async def delete_comment(db: AsyncSession, comment_id: int, user_id: int):
    query = select(Comment).where(
        Comment.id == comment_id, Comment.is_delete == False
    )
    res = await db.execute(query)
    comment = res.scalar_one_or_none()
    if not comment:
        return None
    if comment.user_id != user_id:
        return "forbidden"
    comment.is_delete = True
    await db.flush()
    return comment