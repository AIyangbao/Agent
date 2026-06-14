from sqlalchemy import Index,Integer,String,Enum,DateTime,ForeignKey,Boolean,Text
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from datetime import datetime
class Base(DeclarativeBase):
    pass
class time_Base(Base):
    __abstract__ = True
    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="修改时间"
    )

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
    is_delete: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False,comment="软删除")

    def __repr__(self):
        return f"<blog(id={self.id},title='{self.title}',content='{self.content}')>"
    
class Blog_tags(Base):
    __tablename__ = "blog_tag"

    __table_args__ = (
        Index("uk_blog_tag", "blog_id", "tag_id"),
    )
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True,comment="博客和标签ID")
    blog_id: Mapped[int] = mapped_column(Integer,ForeignKey('blog.id',onupdate='CASCADE',ondelete='CASCADE'),nullable=False,comment="博客ID")
    tag_id: Mapped[int] = mapped_column(Integer,ForeignKey('tag.id',onupdate='CASCADE'),nullable=False,comment="标签ID")

class tag(Base):
    __tablename__ = "tag"

    __table_args__ = (
        Index("uk_name", "name"),
    )
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True,comment="标签ID")
    name: Mapped[str] = mapped_column(String(50),unique=True,nullable=False,comment="标签名")
    create_time: Mapped[datetime] = mapped_column(DateTime,default=datetime.now,comment="创建时间")
    is_delete: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False,comment="软删除")
