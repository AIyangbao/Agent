# my_blog 部署文档（DEPLOY.md）

> 适用对象：从零把项目跑起来 / 迁移到新机器 / 重装环境
> 维护约定：本文档只描述「部署与运维」，不写业务代码细节。后端代码改动请走「先给示例、开发者手动落」的流程。

---

## 1. 项目概览

| 层 | 技术 | 说明 |
|----|------|------|
| 前端 | Vue3 + Vite6 + nginx | 目录名为 **`fontend`**（少一个 n，是历史拼写，别改） |
| 后端 | FastAPI (Python 3.12) + uvicorn | `blog_backend/` |
| 数据库 | MySQL 8.0（Docker） | 数据卷持久化 |
| 缓存/队列 | Redis 7（Docker） | 短信验证码、业务缓存 |
| 编排 | docker compose v2 | 一个 `docker-compose.yml` 起全部 |

架构（请求流）：
```
浏览器 → nginx(:80/:443) → 前端静态资源 / 反代 /api/* → backend(:8000 内网) → MySQL / Redis
```

---

## 2. 环境准备

- **Docker Desktop**（Windows / macOS）或 Docker Engine（Linux），compose v2。
- **Git**（Windows 建议在 **Git Bash** 终端里执行所有 `.sh` 脚本，见 §10 坑位）。
- 阿里云 **DashScope API Key**（通义千问，AI 对话用，没有也能起服务，只是 AI 功能不可用）。
- 一个域名 + SSL 证书（已配置 `blog.fireflyai.site`，证书放 `./ssl/`）。

---

## 3. 目录结构（部署相关）

```
my_blog/
├─ docker-compose.yml          # 编排：mysql / redis / backend / frontend
├─ .env                        # 真实密钥（不提交，必须有）
├─ .env.example                # 变量模板（提交）
├─ backup_mysql.sh             # MySQL 自动备份脚本
├─ blog_backend/
│  ├─ Dockerfile               # 后端镜像（已改成非 root 运行）
│  ├─ docker_entrypoint.sh     # 启动入口：chown 挂载卷 + 降权
│  ├─ requirements.txt         # 依赖已锁版本（可复现构建）
│  └─ ...
├─ fontend/                    # 注意拼写：fontend（少 n）
│  ├─ Dockerfile
│  ├─ nginx.conf               # 含限流 + 安全响应头
│  └─ ...
├─ ssl/                        # SSL 证书（不提交）
└─ backups/                    # 自动备份输出（不提交，已 gitignore）
```

---

## 4. 配置 `.env`

复制模板并填入真实值：

```bash
cp .env.example .env
# 然后编辑 .env 填入真实密钥
```

### 完整变量清单

> ⚠️ `.env.example` 目前**只列了 5 项**，下面带 ★ 的两项是后来加的，example 里没有，请手动补进你自己的 `.env`（部署必须）。

| 变量 | 示例 | 说明 |
|------|------|------|
| `DB_PWD` | `复杂密码` | MySQL root 密码，**必填** |
| `DB_NAME` | `blog_db` | 数据库名 |
| `JWT_PWD` | `一段32位以上随机串` | JWT 签名密钥，**必填** |
| `DASHSCOPE_API_KEY` | `sk-xxxx` | 通义千问 Key，没有则 AI 功能不可用 |
| `QWEN_MODEL` | `qwen-plus` | 模型名 |
| `CORS_ORIGINS` ★ | `["https://blog.fireflyai.site","http://localhost:80"]` | **必须是 JSON 数组字符串**（见 §10 坑位 C） |
| `SMS_MOCK` ★ | `true` 或 `false` | 短信验证码是否走 mock（true=不真发短信，直接返回验证码） |

> **⚠️ 生产短信需企业账号**：阿里云 / 腾讯云短信服务均要求**企业实名认证**才能申请签名与模板，个人实名账号无入口。因此本项目默认 `SMS_MOCK=true`（开发/演示走 mock）。真实发送需：① 企业账号；② 在 `docs/sms_real.md` 落地服务商 SDK（异步 `to_thread` 调用）；③ 配置 `SMS_ACCESS_KEY_ID/SECRET/SIGN_NAME/TEMPLATE_CODE` 并将 `SMS_MOCK` 置 `false`。前端无需改动。

`.env` 会被两路加载：
- **本地开发**：代码里 `load_dotenv()` 读取。
- **容器部署**：compose 的 `env_file: [.env]` 注入 backend 容器（配合 pydantic-settings）。

---

## 5. 首次部署

### 5.1 登录私有镜像仓库（仅首次 / 换机器）
MySQL 镜像是阿里云 ACR **私有**镜像，首次拉取前必须登录，否则 mysql 容器永远起不来、backend 因 `depends_on: service_healthy` 卡住：

```bash
docker login crpi-9640jlmu7u6aesbj.cn-guangzhou.personal.cr.aliyuncs.com
# 输入 ACR 用户名/密码
```

> backend / frontend 镜像是本地 `build` 出来的，不需要登录。

### 5.2 启动全部服务
```bash
cd F:\Agent\my_blog        # 仓库根
docker compose up -d --build
```

### 5.3 验证
```bash
docker compose ps
# 期望：mysql / redis / backend / frontend 全是 healthy 或 Up
```

健康检查端点：
```bash
curl http://localhost:8000/health      # 返回 {"status":"ok"} 等
```

前端访问：`https://blog.fireflyai.site`（或本机 `https://localhost`，需证书）。

---

## 6. 服务与端口

| 服务 | 容器内端口 | 宿主机映射 | 说明 |
|------|-----------|-----------|------|
| frontend (nginx) | 80 / 443 | `80:80` `443:443` | 必须空闲；绑定 80 在 Linux 需 root，Windows 用管理员 |
| backend | 8000 | 不暴露 | 只走 blog-network 内网 `backend:8000` |
| mysql | 3306 | `3307:3306` | 宿主机用 3307 连接，避免和本机 MySQL 冲突 |
| redis | 6379 | 不暴露 | 只走内网 `redis:6379` |

---

## 7. 生产级安全加固清单（已落地）

| 项 | 做法 | 文件 |
|----|------|------|
| 依赖可复现 | `requirements.txt` 全部锁死版本 | `blog_backend/requirements.txt` |
| 后端非 root | 建 `appuser`(uid 1000)，entrypoint 内 chown 挂载卷 + `setpriv` 降权 | `Dockerfile` / `docker_entrypoint.sh` |
| 前端限流 | 短信接口 `limit_req` 1r/s burst=3 | `fontend/nginx.conf` |
| 前端安全头 | HSTS / `X-Content-Type-Options` / `X-Frame-Options` / `Referrer-Policy` | `fontend/nginx.conf` |
| 前端 XSS | markdown 渲染 `escapeHtml` 补引号转义 + `safeUrl` 协议白名单（拦 `javascript:`） | `fontend/src/utils/markdown.js` |
| CORS 白名单 | `CORS_ORIGINS` 仅放行已知域名 | `.env` + `settings.py` |
| 短信防爆 | 60s 冷却 + 一次性销毁 + 失败锁定（redis） | `services/sms_service.py` + `ratelimit_service.py` |

> 验证后端是否真非 root：
> ```bash
> docker compose top backend
> # PID 1 的 uvicorn 进程 UID 应为 1000（appuser），不是 0(root)
> ```
> ⚠️ `docker compose exec backend whoami` **永远返回 root**（exec 默认以 root 进容器），不能用来验证应用用户。

---

## 8. 数据库变更管理

`Base.metadata.create_all` **只会建不存在的表，不会给已存在的表加列**。

如果给 `user` 等表加了字段（如个人中心的 `nickname`/`avatar`/`bio`），对已存在的旧库必须手动补列：

```sql
ALTER TABLE `user`
  ADD COLUMN `nickname` VARCHAR(50)  NULL,
  ADD COLUMN `avatar`   VARCHAR(512) NULL,
  ADD COLUMN `bio`      VARCHAR(500) NULL;
```

报错说「列已存在」就说明不用补（库是加列之后建的）。

---

## 9. 备份与恢复

### 9.1 手动备份
脚本用 `docker exec blog-mysql mysqldump` 热备，读 `.env` 取密码，输出 gzip 到 `backups/`，保留 7 天。

```bash
cd F:\Agent\my_blog
bash ./backup_mysql.sh          # ⚠️ 必须用 Git Bash，不能在 PowerShell 直接 ./xxx.sh
ls backups/                     # 应看到 blog_db_YYYYMMDD_HHMMSS.sql.gz
```

### 9.2 定时任务
**Windows（无 cron）**：用「任务计划程序」每天 04:00 跑：
- 程序：`C:\Program Files\Git\bin\bash.exe`
- 参数：`F:\Agent\my_blog\backup_mysql.sh`
- 建议勾选「不管用户是否登录都要运行」

或用 PowerShell 一行：
```powershell
schtasks /create /tn "BlogMysqlBackup" /tr '"C:\Program Files\Git\bin\bash.exe" "F:\Agent\my_blog\backup_mysql.sh"' /sc daily /st 04:00
```

**Linux / 阿里云 ECS**：用真正的 cron
```bash
crontab -e
# 加：0 4 * * * /path/to/backup_mysql.sh >> /var/log/blog_backup.log 2>&1
```

### 9.3 恢复
```bash
# 在 Git Bash 里解压并导入
gunzip -c backups/blog_db_YYYYMMDD_HHMMSS.sql.gz | docker exec -i blog-mysql mysql -uroot -p"$DB_PWD" blog_db
```

---

## 10. 常见坑位（排障速查）

- **A. MySQL 一直 healthy 不了 / backend 卡在 waiting**
  → 没 `docker login` ACR 私有仓库，mysql 镜像拉不下来。见 §5.1。

- **B. 前端改了没生效**
  → 容器里的前端是构建产物，必须重建：`docker compose build --no-cache frontend && docker compose up -d frontend`，浏览器 **Ctrl+Shift+R** 硬刷。

- **C. 后端启动报 `CORS_ORIGINS` SettingsError**
  → pydantic-settings 2.x 把 list 字段强制 `json.loads` 解析。**`.env` 里必须写 JSON 数组**，不能写逗号分隔：
  ```ini
  # 正确
  CORS_ORIGINS=["https://blog.fireflyai.site","http://localhost:80"]
  # 错误（会崩）
  CORS_ORIGINS=https://blog.fireflyai.site,http://localhost:80
  ```

- **D. `SMS_MOCK` 空值 / bool 解析报错**
  → `.env` 里 `SMS_MOCK` 必须有值（`true`/`false`），不能留空。

- **E. Windows 下 `./backup_mysql.sh` 没反应 / 乱码**
  → PowerShell 不识别 shebang，且 `bash` 在 PowerShell 里中文乱码。**必须进 Git Bash 终端**执行。

- **F. `docker exec backend whoami` 返回 root**
  → 假象，exec 默认 root。验证应用用户用 `docker compose top backend`（看 PID 1 的 UID）。

- **G. 目录找不到**
  → 前端目录是 `fontend`（少 n），别拼成 `frontend`。

---

## 11. 上线验证清单

- [ ] `docker compose ps` 四个服务全 healthy
- [ ] `curl /health` 返回正常
- [ ] 前端 HTTPS 可访问，证书有效
- [ ] `docker compose top backend` 显示 uvicorn UID=1000（非 root）
- [ ] 注册 / 登录 / 个人中心（改头像、昵称、简介、密码）全通
- [ ] 短信验证码发送有 60s 冷却、限流生效
- [ ] `bash ./backup_mysql.sh` 能生成备份文件
- [ ] 定时备份任务已创建并手动触发成功一次
- [ ] `.env` 不提交、`backups/` 不提交（已在 `.gitignore`）

---

## 12. 迁移 / 重装到新机器

1. 装 Docker Desktop / Docker Engine。
2. 拉代码：`git clone ... && cd my_blog`。
3. `cp .env.example .env` 并填真实密钥（补 §4 的 ★ 两项）。
4. `docker login` ACR 私有仓库（§5.1）。
5. `docker compose up -d --build`。
6. 若旧库有数据要迁移：先用 §9.3 在旧机器导出，再新机器导入；新库首次启动会自动 `create_all` 建表。
7. 挂备份定时任务（§9.2）。
```
