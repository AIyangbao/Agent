# 博客系统后端 API 文档 v1.0

---

## 概述

- **基础地址**: `http://127.0.0.1:8000`
- **认证方式**: JWT Bearer Token（`Authorization: Bearer <token>`）
- **数据格式**: JSON
- **字符编码**: UTF-8

---

## 统一响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "操作成功描述",
  "data": { ... }
}
```

### 错误响应

| HTTP 状态码 | code | 说明 |
|:---|:---|:---|
| 400 | 400 | 请求参数错误 / 数据约束冲突（如用户名重复、外键不存在） |
| 401 | 401 | Token 无效、过期或未提供 |
| 404 | 404 | 资源不存在 |
| 500 | 500 | 服务器内部错误 / 数据库操作异常 |

错误响应示例：
```json
{
  "code": 401,
  "message": "Token 已过期",
  "data": null
}
```

---

## 一、用户模块 `/api/user`

### 1. 用户注册

```
POST /api/user/register
```

**认证要求**: 无

**请求体**:
```json
{
  "username": "string (必填，最长50字符)",
  "password": "string (必填，最长72字节)"
}
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "message": "用户注册成功",
  "data": {
    "access_token": "eyJhbGciOi...",
    "username": "admin"
  }
}
```

**错误情况**:
| 状态码 | 说明 |
|:---|:---|
| 400 | 用户名已存在 |

> **注意**: 注册成功后自动返回 JWT Token，无需重新登录。

---

### 2. 用户登录

```
POST /api/user/login
```

**认证要求**: 无

**请求体**:
```json
{
  "username": "string (必填)",
  "password": "string (必填)"
}
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "message": "用户登录成功",
  "data": {
    "access_token": "eyJhbGciOi..."
  }
}
```

**错误情况**:
| 状态码 | 说明 |
|:---|:---|
| 401 | 用户名或密码错误 |

> **Token 有效期**: 3 天

---

### 3. 修改密码

```
PUT /api/user/password
```

**认证要求**: 无（预留接口，暂未实现）

**状态**: 占位接口，当前返回空。

---

## 二、博客模块 `/api/blogs`

### 1. 获取博客列表

```
GET /api/blogs/list_blogs
```

**认证要求**: 无

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|:---|:---|:---|:---|:---|
| `tagId` | int | 否 | `null` | 按标签ID筛选，不传则查全部 |
| `page` | int | 否 | `1` | 页码（从 1 开始） |
| `pageSize` | int | 否 | `10` | 每页数量（最大 100） |

**请求示例**:
```
GET /api/blogs/list_blogs?tagId=3&page=1&pageSize=10
GET /api/blogs/list_blogs?page=1&pageSize=5
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "message": "获取博客列表成功",
  "data": {
    "list": [
      {
        "Blog": {
          "id": 1,
          "title": "文章标题",
          "content": "文章内容...",
          "user_id": 1,
          "is_delete": false,
          "create_time": "2026-06-19T15:30:00",
          "update_time": "2026-06-19T15:30:00"
        },
        "name": "Python"
      }
    ],
    "total": 25
  }
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `data.list` | Array | 博客列表（按创建时间倒序） |
| `data.list[].Blog` | Object | Blog 数据库模型对象 |
| `data.list[].Blog.id` | int | 博客 ID |
| `data.list[].Blog.title` | string | 标题 |
| `data.list[].Blog.content` | string | 正文内容 |
| `data.list[].Blog.user_id` | int | 作者 ID |
| `data.list[].Blog.is_delete` | bool | 软删除标记 |
| `data.list[].Blog.create_time` | string | 创建时间 (ISO 8601) |
| `data.list[].Blog.update_time` | string | 修改时间 (ISO 8601) |
| `data.list[].name` | string | 标签名称（一条博客有多个标签时会出现多条记录） |
| `data.total` | int | 符合条件的博客总数 |

---

### 2. 获取博客详情

```
GET /api/blogs/detail
```

**认证要求**: 无

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| `id` | int | 是 | 博客 ID |

**请求示例**:
```
GET /api/blogs/detail?id=1
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "message": "获取博客详情成功",
  "data": {
    "blog": {
      "id": 1,
      "title": "文章标题",
      "content": "完整的文章内容...",
      "user_id": 1,
      "is_delete": false,
      "create_time": "2026-06-19T15:30:00",
      "update_time": "2026-06-19T15:30:00"
    },
    "tags": ["Python", "FastAPI", "Vue3"]
  }
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `data.blog` | Object | 博客详情 |
| `data.tags` | Array[string] | 标签名称列表 |

**错误情况**:
| 状态码 | 说明 |
|:---|:---|
| 422 | 缺少必填参数 `id` 或格式错误 |

---

### 3. 添加博客（需认证）

```
POST /api/blogs/add
```

**认证要求**: Bearer Token（需要已登录用户）

**请求头**:
```
Authorization: Bearer eyJhbGciOi...
Content-Type: application/json
```

**请求体**:
```json
{
  "title": "string (必填，最长255字符)",
  "content": "string (必填)",
  "user_id": 0,
  "tag_ids": [1, 2, 3]
}
```

| 字段 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| `title` | string | 是 | 博客标题 |
| `content` | string | 是 | 博客正文 |
| `user_id` | int | 是 | 作者ID（由后端自动覆写为当前登录用户ID，传任意值均可） |
| `tag_ids` | Array[int] | 否 | 关联标签的 ID 列表 |

**成功响应 (200)**:
```json
{
  "code": 200,
  "message": "添加博客成功",
  "data": {
    "_sa_instance_state": "...",
    "title": "新文章",
    "content": "内容...",
    "user_id": 1,
    "id": 7
  }
}
```

**错误情况**:
| 状态码 | 说明 |
|:---|:---|
| 401 | Token 无效、过期或未提供 |
| 422 | 参数校验失败（缺少必填字段） |

---

### 4. 修改博客（需认证）

```
PUT /api/blogs/update
```

**认证要求**: Bearer Token

**请求头**:
```
Authorization: Bearer eyJhbGciOi...
Content-Type: application/json
```

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| `id` | int | 是 | 要修改的博客 ID |

**请求体**:
```json
{
  "title": "修改后的标题",
  "content": "修改后的内容"
}
```

| 字段 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| `title` | string | 否 | 新标题（不传则不修改） |
| `content` | string | 否 | 新内容（不传则不修改） |

> **注意**: 只更新请求体中传递的字段，未传字段保持原值不变。

**请求示例**:
```
PUT /api/blogs/update?id=7
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "message": "修改博客成功",
  "data": {
    "blog": { ... },
    "tags": ["Python"]
  }
}
```

**错误情况**:
| 状态码 | 说明 |
|:---|:---|
| 401 | Token 无效、过期或未提供 |
| 404 | 博客不存在 |

---

### 5. 删除博客（需认证）

```
DELETE /api/blogs/delete
```

**认证要求**: Bearer Token

**请求头**:
```
Authorization: Bearer eyJhbGciOi...
```

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| `id` | int | 是 | 要删除的博客 ID |

**请求示例**:
```
DELETE /api/blogs/delete?id=7
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "message": "删除博客成功",
  "data": null
}
```

**错误情况**:
| 状态码 | 说明 |
|:---|:---|:---|
| 401 | Token 无效、过期或未提供 |
| 404 | 博客不存在 |

> **注意**: 删除为软删除（设置 `is_delete=true`），数据不会从数据库中物理删除。

---

## 三、认证说明

### 认证流程

```
1. POST /api/user/register  →  注册后自动获取 token
2. POST /api/user/login     →  登录后获取 token
3. 后续需认证的请求头中携带: Authorization: Bearer <token>
```

### Token 结构

- **算法**: HS256
- **有效期**: 3 天
- **Payload**:
  ```json
  {
    "sub": "用户ID",
    "exp": 过期时间戳
  }
  ```

---

## 四、数据模型

### Blog（博客）

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `id` | int | 主键，自增 |
| `title` | String(255) | 标题 |
| `content` | Text | 正文 |
| `user_id` | int | 作者ID（外键 → user.id） |
| `is_delete` | bool | 软删除标记（默认 false） |
| `create_time` | datetime | 创建时间（自动填充） |
| `update_time` | datetime | 修改时间（自动更新） |

### User（用户）

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `id` | int | 主键，自增 |
| `username` | String(50) | 用户名（唯一） |
| `password` | String(255) | 密码（bcrypt 加密存储） |
| `is_delete` | bool | 软删除标记 |
| `create_time` | datetime | 创建时间 |
| `update_time` | datetime | 修改时间 |

### Tag（标签）

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `id` | int | 主键，自增 |
| `name` | String(50) | 标签名（唯一） |
| `create_time` | datetime | 创建时间 |
| `is_delete` | bool | 软删除标记 |

### Blog-Tag 关联表

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `id` | int | 主键 |
| `blog_id` | int | 博客ID（外键） |
| `tag_id` | int | 标签ID（外键） |

---

## 五、接口汇总

| 方法 | 路径 | 认证 | 说明 |
|:---|:---|:---|:---|
| POST | `/api/user/register` | 无 | 用户注册 |
| POST | `/api/user/login` | 无 | 用户登录 |
| PUT | `/api/user/password` | 无 | 修改密码（预留） |
| GET | `/api/blogs/list_blogs` | 无 | 博客列表（分页+标签筛选） |
| GET | `/api/blogs/detail` | 无 | 博客详情 |
| POST | `/api/blogs/add` | 是 | 添加博客 |
| PUT | `/api/blogs/update` | 是 | 修改博客 |
| DELETE | `/api/blogs/delete` | 是 | 删除博客（软删除） |

---

## 六、部署说明

### 环境变量（.env）

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PWD=your_password
DB_NAME=blog_db
JWT_PWD=your_jwt_secret_key
```

### 启动命令

```bash
# 确保虚拟环境已激活
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 依赖项

- Python 3.10+
- FastAPI + Uvicorn
- SQLAlchemy (async) + asyncmy (MySQL)
- PyJWT + passlib[bcrypt]
- Pydantic + pydantic-settings

### 部署前检查

1. MySQL 服务运行中，数据库 `blog_db` 已创建
2. 初始化脚本 `scripts/init_db.py` 已执行（创建表结构 + 初始标签数据）
3. `.env` 配置正确（数据库连接 + JWT 密钥）
4. 生产环境建议修改 `utils/exception.py` 中 `DEBUG_MODE = False`

---

> 文档版本: v1.0 | 最后更新: 2026-06-19
