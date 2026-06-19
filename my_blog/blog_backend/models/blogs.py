from sqlalchemy import Index,Integer,String,Enum,DateTime,ForeignKey,Boolean,Text,func,text
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime
from config.base import time_Base


class Blog(time_Base):
    __tablename__ = "blog"

    # 创建索引: 提升查询速度 -> 添加目录
    __table_args__ = (
        Index("idx_title","title"),
        Index("idx_user_id","user_id")
    )
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True,comment="博客ID")
    title: Mapped[str] = mapped_column(String(255),nullable=False,comment="博客标题")
    content: Mapped[str] = mapped_column(Text,nullable=False,comment="文章内容")
    user_id: Mapped[int] = mapped_column(Integer,ForeignKey('user.id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False,comment="作者ID")
    is_delete: Mapped[bool] = mapped_column(Boolean,server_default=text("0"),nullable=False,comment="软删除")

    def __repr__(self):
        return f"<blog(id={self.id},title='{self.title}',content='{self.content}')>"
    

