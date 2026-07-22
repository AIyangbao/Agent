# 使用 Python 3.12 slim 镜像
# asyncmy 在 PyPI 有 cp312 预编译 .whl，不需要 gcc
FROM python:3.12-slim

ENV TZ=Asia/Shanghai
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 不需要 gcc！asyncmy 用预编译 Wheel 安装，秒级完成
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY . .

# 暴露端口（仅声明，实际映射在 compose 里配）
EXPOSE 8000

# 用 Python 脚本启动（避开 shell 换行符坑）
CMD ["python", "-u", "docker_start.py"]