from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import Boolean, String, Integer, text
from config.base import time_Base


class User(time_Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="用户ID"
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="用户名"
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码(加密存储)"
    )
    phone: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=True, index=True, comment="手机号(验证码登录)"
    )
    nickname: Mapped[str] = mapped_column(
        String(50), nullable=True, comment="呢称"
    )
    avatar: Mapped[str] = mapped_column(
        String(512), nullable=True, comment="头像URL"
    )
    bio: Mapped[str] = mapped_column(
        String(500), nullable=True, comment="个人简介"
    )
    is_delete: Mapped[bool] = mapped_column(
        Boolean, server_default=text("0"), comment="软删除"
    )
