from sqlalchemy import Index, Integer, String, DateTime, ForeignKey, Boolean, func, text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from config.base import Base


class Blog_tags(Base):
    __tablename__ = "blog_tag"

    __table_args__ = (Index("uk_blog_tag", "blog_id", "tag_id", unique=True),)
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="博客和标签ID"
    )
    blog_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("blog.id", ondelete="CASCADE"),
        nullable=False,
        comment="博客ID",
    )
    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tag.id", onupdate="CASCADE"),
        nullable=False,
        comment="标签ID",
    )


class tag(Base):
    __tablename__ = "tag"

    __table_args__ = (Index("uk_name", "name"),)
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="标签ID"
    )
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="标签名"
    )
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    is_delete: Mapped[bool] = mapped_column(
        Boolean, server_default=text("0"), nullable=False, comment="软删除"
    )
