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

# ========== 非 root 用户（生产安全） ==========
# 默认容器以 root 跑应用代码，一旦被攻破后果严重。
# 这里创建一个普通用户 appuser(uid 1000)，把 /app 交给他。
RUN useradd -m -u 1000 appuser \
 && chown -R appuser:appuser /app

# 启动脚本：先把挂载的数据卷目录改属主（已存在卷可能属 root），
# 再以 appuser 身份运行后端，避免权限问题。
COPY docker_entrypoint.sh /usr/local/bin/docker_entrypoint.sh
RUN chmod +x /usr/local/bin/docker_entrypoint.sh

# 暴露端口（仅声明，实际映射在 compose 里配）
EXPOSE 8000

# 用 entrypoint 脚本启动（脚本内部降级到非 root）
ENTRYPOINT ["/usr/local/bin/docker_entrypoint.sh"]