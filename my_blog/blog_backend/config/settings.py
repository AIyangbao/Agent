from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_parse_list=True)
    # 数据库
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT"))
    DB_USER: str = os.getenv("DB_USER")
    DB_PWD: str = os.getenv("DB_PWD")
    DB_NAME: str = os.getenv("DB_NAME")
    # JWT
    JWT_PWD: str = os.getenv("JWT_PWD")
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST","localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT","6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB","0"))
    # DEBUG
    DEBUG: bool = os.getenv("DEBUG_MODE","False") == "True"
    # AI
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY","")
    QWEN_MODEL: str = os.getenv("QWEN_MODEL","qwen-plus")
    #CORS
    CORS_ORIGINS: list[str] = ["*"]
    # SMS
    SMS_MOCK: bool = True
    # 手机号加密密钥
    PHONE_ENCRYPTION_KEY: str = os.getenv("PHONE_ENCRYPTION_KEY")

    # 拼接异步数据库连接URL
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PWD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"


# 全局单例配置
settings = Settings()
