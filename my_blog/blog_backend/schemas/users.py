from typing import Optional

from pydantic import BaseModel,Field,ConfigDict

class UserRequest(BaseModel):
    username: str
    password: str

class UserChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

