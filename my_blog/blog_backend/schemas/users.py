
from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):
    username: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=1, max_length=200)


class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=1, max_length=200)

class UserProfileUpdate(BaseModel):
    nickname: str| None = Field(default=None, max_length=50)
    avatar: str | None = Field(default=None, max_length=512)
    bio: str | None = Field(default=None, max_length=500)

class UserMe(BaseModel):
    id: int
    username: str
    nickname: str | None = None
    avatar: str | None = None
    bio: str | None = None
    phone: str | None = None
    model_config = ConfigDict(from_attributes=True)
