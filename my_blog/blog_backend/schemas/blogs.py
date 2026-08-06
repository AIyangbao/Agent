from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class BlogCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    content: str = Field(..., min_length=1, max_length=50000, description="内容")
    tag_ids: Optional[List[int]] = None
    tag_names: Optional[List[str]] = None


class BlogUpdate(BaseModel):
    title: Optional[str] = Field(..., min_length=1, max_length=200, description="标题")
    content: Optional[str] = Field(..., min_length=1, max_length=50000, description="内容")


class BlogResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    tags_name: List[str]
    create_time: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
