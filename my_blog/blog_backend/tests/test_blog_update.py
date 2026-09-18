"""
update_blog 编辑功能测试（v6.1）

覆盖三块语义（对应 后端技术文档.md §1 v6.1 变更记录）：
1. 只改标题/正文，不传标签字段 → 关联表不动
2. 标签重绑：tag_names 自动新建 / tag_ids 过滤无效 / 空数组清空 / 双字段取并集
3. 权限与边界：非作者 403、文章不存在 404、detail 返回 create_time

标签预置（conftest.setup_db）：id 1-5 = Python / AI / Vue / Docker / FastAPI
"""
import pytest


# ---------- 公共小工具 ----------

async def _create_post(client, title="原标题", content="原内容", tag_names=None):
    """发文并返回 (blog_id, detail_data)。tag_names 默认带 Python+AI 便于观察重绑。"""
    body = {"title": title, "content": content}
    if tag_names is not None:
        body["tag_names"] = tag_names
    resp = await client.post("/api/blogs/add", json=body)
    assert resp.status_code == 200, f"发文失败: {resp.text}"
    blog_id = resp.json()["data"]["id"]

    detail = await client.get("/api/blogs/detail", params={"id": blog_id})
    assert detail.status_code == 200, f"详情失败: {detail.text}"
    return blog_id, detail.json()["data"]


def _tag_names(detail: dict) -> set:
    return set(detail.get("tags_name") or [])


# ---------- 1. 只改正文，标签不动 ----------

@pytest.mark.asyncio
async def test_update_content_keeps_tags(auth_client_a):
    """不传任何标签字段 → 标签保持原样（is not None 守卫的正面用例）"""
    blog_id, before = await _create_post(auth_client_a, tag_names=["Python", "AI"])

    resp = await auth_client_a.put(
        "/api/blogs/update",
        params={"id": blog_id},
        json={"title": "新标题", "content": "新内容"},   # 注意：没有 tag 字段
    )
    assert resp.status_code == 200, resp.text

    after = (await auth_client_a.get("/api/blogs/detail", params={"id": blog_id})).json()["data"]
    assert after["title"] == "新标题"
    assert after["content"] == "新内容"
    assert _tag_names(after) == {"Python", "AI"}, "没传标签字段，原标签必须原样保留"


# ---------- 2. 标签重绑 ----------

@pytest.mark.asyncio
async def test_update_tag_names_creates_new_tag(auth_client_a):
    """tag_names 里带库中不存在的名字 → 自动新建并绑定（本次真正的行为升级）"""
    blog_id, _ = await _create_post(auth_client_a, tag_names=["Python"])

    resp = await auth_client_a.put(
        "/api/blogs/update",
        params={"id": blog_id},
        json={"title": "t", "content": "c", "tag_names": ["Redis"]},
    )
    assert resp.status_code == 200, resp.text

    after = (await auth_client_a.get("/api/blogs/detail", params={"id": blog_id})).json()["data"]
    assert _tag_names(after) == {"Redis"}, "删旧+插新后应只剩新标签"


@pytest.mark.asyncio
async def test_update_tag_ids_filters_invalid(auth_client_a):
    """tag_ids 混入不存在的 id → 静默过滤，只绑有效的"""
    blog_id, _ = await _create_post(auth_client_a, tag_names=["AI"])

    resp = await auth_client_a.put(
        "/api/blogs/update",
        params={"id": blog_id},
        json={"title": "t", "content": "c", "tag_ids": [1, 99999]},
    )
    assert resp.status_code == 200, resp.text

    after = (await auth_client_a.get("/api/blogs/detail", params={"id": blog_id})).json()["data"]
    assert _tag_names(after) == {"Python"}, "99999 不存在，应只保留 id=1(Python)"


@pytest.mark.asyncio
async def test_update_empty_tag_names_clears_tags(auth_client_a):
    """显式传空数组 = 清空标签（if tag_ids: 会吞掉这个语义，必须 is not None 判断）"""
    blog_id, _ = await _create_post(auth_client_a, tag_names=["Python", "Docker"])

    resp = await auth_client_a.put(
        "/api/blogs/update",
        params={"id": blog_id},
        json={"title": "t", "content": "c", "tag_names": []},
    )
    assert resp.status_code == 200, resp.text

    after = (await auth_client_a.get("/api/blogs/detail", params={"id": blog_id})).json()["data"]
    assert _tag_names(after) == set(), "显式传 [] 必须清空，而不是被当成'没传'"


@pytest.mark.asyncio
async def test_update_ids_and_names_union(auth_client_a):
    """tag_ids + tag_names 同传 → 取并集（同名字去重）"""
    blog_id, _ = await _create_post(auth_client_a, tag_names=["Python"])

    resp = await auth_client_a.put(
        "/api/blogs/update",
        params={"id": blog_id},
        json={"title": "t", "content": "c", "tag_ids": [1], "tag_names": ["Vue", "Python"]},
    )
    assert resp.status_code == 200, resp.text

    after = (await auth_client_a.get("/api/blogs/detail", params={"id": blog_id})).json()["data"]
    assert _tag_names(after) == {"Python", "Vue"}, "id=1(Python) 与 names(Vue,Python) 应取并集去重"


# ---------- 3. 权限 / 边界 / 字段回显 ----------

@pytest.mark.asyncio
async def test_update_by_non_owner_403(auth_client_a, auth_client_b):
    """B 编辑 A 的文章 → 403（拦截在路由层，还没到 curd）"""
    blog_id, _ = await _create_post(auth_client_a, tag_names=["Python"])

    resp = await auth_client_b.put(
        "/api/blogs/update",
        params={"id": blog_id},
        json={"title": "被篡改", "content": "hacked"},
    )
    assert resp.status_code == 403, resp.text

    after = (await auth_client_a.get("/api/blogs/detail", params={"id": blog_id})).json()["data"]
    assert after["title"] == "原标题", "403 之后内容不能被改动"


@pytest.mark.asyncio
async def test_update_not_found_404(auth_client_a):
    """编辑不存在的文章 → 404"""
    resp = await auth_client_a.put(
        "/api/blogs/update",
        params={"id": 99999},
        json={"title": "t", "content": "c"},
    )
    assert resp.status_code == 404, resp.text


@pytest.mark.asyncio
async def test_detail_returns_create_time(auth_client_a):
    """get_blog_detail 必须回传 create_time（修'未知日期'的回归测试）"""
    _, detail = await _create_post(auth_client_a, tag_names=["Python"])
    assert detail.get("create_time"), "create_time 不应为 null/缺失，否则前端显示'未知日期'"
