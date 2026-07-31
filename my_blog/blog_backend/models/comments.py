from sqlalchemy import Integer, Text, ForeignKey, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column
from config.base import time_Base

class Comment(time_Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="评论ID")
    blog_id: Mapped[int] = mapped_column(
                                         Integer,
                                         ForeignKey("blog.id", ondelete="CASCADE", onupdate="CASCADE"),
                                         nullable=False,
                                         comment="所属博客ID",
                                         )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="评论者ID",
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="评论内容")
    parent_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("comment.id", ondelete="CASCADE"),
        nullable=True,
        comment="父评论ID(用于回复)",
    )
    is_delete: Mapped[bool] = mapped_column(
        Boolean, server_default=text("0"), nullable=False, comment="软删除"
    )

    def __repr__(self):
        return f"<comment(id={self.id},blog_id={self.blog_id})>"