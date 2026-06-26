"""Docker 启动脚本：等待 MySQL → 初始化数据库 → 启动 FastAPI"""

import asyncio
import subprocess
import sys
import os
from time import sleep


async def check_mysql():
    """直接用 asyncmy 检测 MySQL"""
    import asyncmy

    conn = await asyncmy.connect(
        host=os.getenv("DB_HOST", "mysql"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PWD"),
        db=os.getenv("DB_NAME", "blog_db"),
    )
    conn.close()
    return True


def wait_for_mysql(max_retries=30):
    print("=== 等待 MySQL 就绪 ===")
    for i in range(max_retries):
        try:
            asyncio.run(check_mysql())
            print("MySQL 连接成功!")
            return True
        except Exception as e:
            print(f"  [{i + 1}/{max_retries}] {e}")
        sleep(2)

    print("ERROR: MySQL 连接超时!")
    return False


def main():
    if not wait_for_mysql():
        sys.exit(1)

    print("=== 初始化数据库 ===")
    subprocess.run([sys.executable, "scripts/init_db.py"], check=True)
    print("=== 数据库初始化完成 ===")

    print("=== 启动 FastAPI ===")
    os.execvp("uvicorn", ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])


if __name__ == "__main__":
    main()
