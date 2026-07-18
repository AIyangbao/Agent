from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from config.base import time_Base

class Music(time_Base):
    __tablename__ = "music"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="歌曲ID"
    )
    title: Mapped[str] = mapped_column(String(255),nullable=False, comment="歌曲名")
    artist: Mapped[str] = mapped_column(
        String(128), nullable=False, server_default="未知歌手",comment="歌手"
    )
    cover: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="封面URL,可为空(前端emoji兜底)"
    )
    src: Mapped[str] = mapped_column(String(512), nullable=False, comment="音频条件URL")

    def __repr__(self):
        return f"<Music(id={self.id}, title='{self.title}')>"