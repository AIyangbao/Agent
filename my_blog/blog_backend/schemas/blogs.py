from pydantic import BaseModel, Field
from typing import Optional, List


class BlogCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    content: str = Field(..., min_length=1, max_length=50000, description="内容")
    tag_ids: Optional[List[int]] = None


class BlogUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    content: str = Field(..., min_length=1, max_length=50000, description="内容")


class BlogResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    tags_name: List[str]

    class Config:
        from_attributes = True
