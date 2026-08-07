#!/bin/sh
# backend 容器启动入口：先把挂载的数据卷改属主，再以非 root 用户启动后端
# 为什么需要这一步：named volume 若是升级前就存在的，目录属主是 root，
# 直接以 appuser 运行会因 Permission denied 写不进 chroma / 上传目录而崩溃。

# 修正挂载卷目录属主（找不到就忽略，不影响启动）
chown -R appuser:appuser /app/chroma_data /app/uploads 2>/dev/null || true

# 切换到非 root 用户（appuser, uid 1000）运行后端主进程
# 优先用 setpriv：它能直接以 appuser 运行 python，使 uvicorn 成为 PID 1，
#   docker stop 时 SIGTERM 能优雅送达；少数精简镜像没有 setpriv 时退回 su。
if command -v setpriv >/dev/null 2>&1; then
  exec setpriv --reuid=1000 --regid=1000 --clear-groups python -u /app/docker_start.py
elif command -v su >/dev/null 2>&1; then
  exec su appuser -s /bin/sh -c "python -u /app/docker_start.py"
else
  # 极端兜底：实在没有降权工具就以 root 跑（不推荐，仅防启动失败）
  exec python -u /app/docker_start.py
fi
