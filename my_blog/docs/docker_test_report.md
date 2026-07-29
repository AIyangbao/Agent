# Docker 部署测试报告

测试时间：2026-07-27
部署架构：mysql + redis + backend(FastAPI) + frontend(nginx) 四容器 docker-compose

## 容器状态（全部 Up）
| 容器 | 状态 | 说明 |
|------|------|------|
| blog-mysql | healthy | 宿主机 3307→容器 3306 |
| blog-redis | healthy | 不暴露宿主机端口，走内网 |
| blog-backend | healthy | uvicorn 0.0.0.0:8000 |
| blog-frontend | Up | nginx 80/443 |

## 接口测试结果（经 nginx localhost:80）

| 接口 | 路径 | 结果 |
|------|------|------|
| 前端首页 | GET / | 200，552 bytes index.html ✅ |
| 健康检查 | GET /api/health | 200，{"status":"ok"} ✅ |
| 博客列表 | GET /api/blogs/list_blogs?page=1&page_size=3 | 200，返回博客数据 ✅ |
| 博客详情 | GET /api/blogs/detail?id=1 | 接口正常（id=1 软删返回404是业务逻辑）✅ |
| RSS | GET /api/blogs/rss | 200，XML ✅ |
| 音乐列表 | GET /api/music/list | 200，返回音乐数据 ✅ |

### 注意
- 博客详情参数名是 `id`（不是 `blog_id`）
- 前端无独立 `/tags` 接口，标签从博客列表 `tags` 字段聚合，属正常设计

## 配置改动记录（本次部署）
1. `docker-compose.yml`：加 backend/frontend `build:` 段；redis 不暴露宿主机端口；删 `version`；backend 加 healthcheck；frontend depends_on 改 service_healthy
2. `fontend/nginx.conf`：proxy_pass 末尾不加 `/`（backend 路由自带 /api 前缀）；加 SSE 支持（proxy_buffering off 等）

## 待用户执行（后端代码，按规则用户自己改）
- `blog_backend/main.py` 需补 `/health` 路由（healthcheck 依赖）：
  ```python
  @app.get("/health")
  async def health():
      return {"status": "ok"}
  ```

## 已知问题
- Docker Desktop WSL 后端偶发卡顿（docker start / compose up 超时），重启 Docker Desktop 可解
- 本地 6379 端口曾被旧 Redis 占用，已通过不暴露 redis 端口规避冲突
