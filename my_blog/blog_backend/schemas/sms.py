from pydantic import BaseModel,Field

class CodeLoginIn(BaseModel):
    phone: str
    code: str

class PhoneIn(BaseModel):
    phone: str = Field(pattern=r"^1[3-9]\d{9}$")