from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from config.base import time_Base

class ChatHistory(time_Base):
    __tablename__ = "chat_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="用户ID")
    role: Mapped[str] = mapped_column(String(20), nullable=False, comment="user/assistant")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    