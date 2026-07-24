import logging
from logging.handlers import RotatingFileHandler
import os

# 日志目录
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 日志格式 (时间、日志器名、级别、消息)
LOG_FORMAT = "%(asctime)s - %(name)s -%(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_log():
    logger = logging.getLogger("blog_backend")
    logger.setLevel(logging.INFO)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 普通日志文件 （按大小切割）
    file_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, "blog.log"),
        maxBytes=50 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    # 错误日志单存在 error.log
    error_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, "error.log"),
        maxBytes=50 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    return logger


# 全局logger对象
logger = setup_log()
