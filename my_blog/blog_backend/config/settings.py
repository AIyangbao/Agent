from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    # 数据库
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT"))
    DB_USER: str = os.getenv("DB_USER")
    DB_PWD: str = os.getenv("DB_PWD")
    DB_NAME: str = os.getenv("DB_NAME")
    # JWT
    JWT_PWD: str = os.getenv("JWT_PWD")
    # 拼接异步数据库连接URL
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PWD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

# 全局单例配置
settings = Settings()