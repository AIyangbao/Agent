from typing import Optional

from pydantic import BaseModel,Field,ConfigDict

class UserRequest(BaseModel):
    username: str
    password: str

