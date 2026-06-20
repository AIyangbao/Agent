#!/bin/bash
set -e

echo "=== 等待 MySQL 就绪 ==="

# 循环检测 MySQL 是否可连
# 虽然 docker-compose 有 depends_on healthcheck，但多一道保险
until python -c "
import asyncio, asyncmy
try:
    asyncio.get_event_loop().run_until_complete(
        asyncmy.connect(host='${DB_HOST}', port=${DB_PORT}, user='${DB_USER}', password='${DB_PWD}', db='${DB_NAME}')
    )
    print('MySQL 连接成功')
except Exception as e:
    print(f'MySQL 未就绪: {e}')
    exit(1)
" 2>/dev/null; do
    echo "等待 MySQL 启动中..."
    sleep 2
done

echo "=== MySQL 已就绪，开始初始化数据库 ==="

# 运行 init_db.py 创建数据表
python scripts/init_db.py

echo "=== 数据库初始化完成，启动 FastAPI ==="

# 启动 uvicorn
# --host 0.0.0.0: 允许外部访问（容器必须）
# --port 8000: 后端端口
# 不加 --reload: 生产环境不需要热重载
exec uvicorn main:app --host 0.0.0.0 --port 8000