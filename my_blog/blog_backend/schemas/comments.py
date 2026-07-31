from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CommentCreate(BaseModel):
    blog_id: int = Field(..., description="博客ID")
    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")
    parent_id: Optional[int] = Field(None, description="父评论,不填则为一级评论")


class CommentResponse(BaseModel):
    id: int
    blog_id: int
    username: str
    content: str
    parent_id: Optional[int] = None
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True