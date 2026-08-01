"""
评论模块测试(v4 核心）：
- 鉴权：未登录不能发/删
- 增：登录可发，空内容 422
- 查：列表含评论+用户名，空博客返回 []
- 删：本人可删(软删)，他人 403,不存在 404
- 回归：发完立刻 list 能读到（锁死 commit 修复，防读后写不一致回潮）
运行: pytest tests/test_comments.py -v
"""
import pytest
from httpx import AsyncClient

async def _create_blog(client: AsyncClient) -> int:
    resp = await client.post(
        "/api/blogs/add",
        json={"title": "评论测试文章", "content": "正文", "tag_ids": [1]},
    )
    assert resp.status_code == 200
    return resp.json()["data"]["id"]

class TestCommentAuth:
    async def test_add_unauthenticated(self, client: AsyncClient):
        resp = await client.post(
            "/api/comments/add", json={"blog_id": 1, "content": "没登录不能评论"}
        )
        assert resp.status_code == 401

    async def test_delete_unauthenticated(self, client: AsyncClient):
        resp = await client.delete("/api/comments/delete?id=1")
        assert resp.status_code == 401


class TestCommentAdd:
    async def test_add_success(self, auth_client_a: AsyncClient):
        blog_id = await _create_blog(auth_client_a)
        resp = await auth_client_a.post(
            "/api/comments/add", json={"blog_id": blog_id, "content": "第一条评论"}
        )
        assert resp.status_code == 200

    async def test_add_empty_content(self, auth_client_a: AsyncClient):
        blog_id = await _create_blog(auth_client_a)
        resp = await auth_client_a.post(
            "/api/comments/add", json={"blog_id": blog_id, "content": ""}
        )
        assert resp.status_code == 422 # schema min_length=1


class TestCommentReadAfterWrite:
    """★ 回归测试:v4 读后写修复的保险丝。"""
    async def test_add_then_list_sees_comment(self, auth_client_a: AsyncClient):
        blog_id = await _create_blog(auth_client_a)
        await auth_client_a.post(
            "/api/comments/add",
            json={"blog_id": blog_id, "content": "即时可见的评论"},
        )
        resp = await auth_client_a.get(f"/api/comments/list?blogId={blog_id}")
        assert resp.status_code == 200
        comments = resp.json()["data"]
        assert any(c["content"] == "即时可见的评论" for c in comments)

class TestCommentList:
    async def test_list_empty(self, auth_client_a: AsyncClient):
        blog_id = await _create_blog(auth_client_a)
        resp = await auth_client_a.get(f"/api/comments/list?blogId={blog_id}")
        assert resp.status_code == 200
        assert resp.json()["data"] == []

    async def test_list_returns_username(self, auth_client_a: AsyncClient):
        blog_id = await _create_blog(auth_client_a)
        await auth_client_a.post(
            "/api/comments/add",json={"blog_id": blog_id, "content": "带用户名"}
        )
        resp = await auth_client_a.get(f"/api/comments/list?blogId={blog_id}")
        assert resp.json()["data"][0]["username"] == "user_a"

class TestCommentDelete:
    async def test_delete_own(self, auth_client_a: AsyncClient):
        blog_id = await _create_blog(auth_client_a)
        await auth_client_a.post(
            "/api/comments/add", json={"blog_id": blog_id, "content": "要删的"}
        )
        cid = (await auth_client_a.get(f"/api/comments/list?blogId={blog_id}")) \
              .json()["data"][0]["id"]
        resp = await auth_client_a.delete(f"/api/comments/delete?id={cid}")
        assert resp.status_code == 200
        # 软删后列表不再含它
        listing = await auth_client_a.get(f"/api/comments/list?blogId={blog_id}")
        assert all(c["id"] != cid for c in listing.json()["data"])

    async def test_delete_others_forbidden(self, auth_client_a, auth_client_b):
        blog_id = await _create_blog(auth_client_a)
        await auth_client_a.post(
            "/api/comments/add", json={"blog_id": blog_id, "content": "A的评论"}
        )
        cid = (await auth_client_a.get(f"/api/comments/list?blogId={blog_id}")) \
        .json()["data"][0]["id"]
        resp = await auth_client_b.delete(f"/api/comments/delete?id={cid}")
        assert resp.status_code == 403

    async def test_delete_not_found(self, auth_client_a):
        resp = await auth_client_a.delete("/api/comments/delete?id=9999")
        assert resp.status_code == 404
