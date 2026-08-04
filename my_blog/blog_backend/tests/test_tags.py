"""
标签相关测试: 通过博客列表 tagId 筛选 + 详情 tags_name
(项目无独立 tags 路由, 标签逻辑在 blogs 模块)
运行: pytest tests/test_tags.py -v
"""
import pytest
from httpx import AsyncClient

class TestTagFilter:
    async def test_list_by_tag_includes_pwn(self, auth_client_a: AsyncClient):
        """发带 tag_ids=[1] 的文章, 按 tagId=1 筛选应能查到"""
        create = await auth_client_a.post(
            "/api/blogs/add",
            json={"title": "标签筛选测试A", "content": "正文", "tag_ids": [1]},
        )
        assert create.status_code == 200
        created_id = create.json()["data"]["id"]
        resp = await auth_client_a.get("/api/blogs/list_blogs?tagId=1&page=1&pageSize=10")
        assert resp.status_code == 200
        ids = [b["id"] for b in resp.json()["data"]["list"]]
        assert created_id in ids

    async def test_list_by_tag_excludes_other(self, auth_client_a: AsyncClient):
        """"发表 tag_ids=[2] 的文章, 按 tagId=1 筛选不应包含它"""
        create = await auth_client_a.post(
            "/api/blogs/add",
            json={"title": "标签筛选测试B", "content": "正文", "tag_ids": [2]},
        )
        created_id = create.json()["data"]["id"]
        resp = await auth_client_a.get("/api/blogs/list_blogs?tagId=1&page=1&pageSize=10")
        ids = [b["id"] for b in resp.json()["data"]["list"]]
        assert created_id not in ids

    async def test_list_by_nonexistent_tag(self, auth_client_a: AsyncClient):
        """按不存在的tagId筛选 -> list为空, total=0"""
        resp = await auth_client_a.get("/api/blogs/list_blogs?tagId=99999&page=1&pageSize=10")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] == 0
        assert data["list"] == []

class TestTagDetail:
    async def test_blog_has_tags_name(self, auth_client_a: AsyncClient):
        """发呆 tag_ids[1]的文章,详情 tags_name 应非空"""
        create = await auth_client_a.post(
            "/api/blogs/add",
            json={"title": "详情标签测试", "content": "正文", "tag_ids": [1]},
        )
        blog_id = create.json()["data"]["id"]
        detail = await auth_client_a.get(f"/api/blogs/detail?id={blog_id}")
        assert detail.status_code == 200
        tags_name = detail.json()["data"]["tags_name"]
        assert isinstance(tags_name, list) and len(tags_name) >= 1

class TestTagCreateByName:
    async def test_create_new_tag_by_name(self, auth_client_a: AsyncClient):
        """传不存在的 tag_names,后端应自动新建标签并关联"""
        new_tag = "量子纠缠测试专用标签"
        create = await auth_client_a.post(
            "/api/blogs/add",
            json={"title":"按名建标签测试", "content": "正文", "tag_names": [new_tag]},
        )
        assert create.status_code == 200
        blog_id = create.json()["data"]["id"]
        # 详情应带上这个新标签
        detail = await auth_client_a.get(f"/api/blogs/detail?id={blog_id}")
        assert detail.status_code == 200
        assert new_tag in detail.json()["data"]["tags_name"]
        # tag/list 应能列出这个新标签
        tags = await auth_client_a.get("/api/tags/list")
        names = [t["name"] for t in tags.json()["data"]]
        assert new_tag in names

    async def test_tag_names_and_ids_merge(self, auth_client_a: AsyncClient):
        """同时传 tag_ids=[1] 与 tag_names=['自定义'],两者都应关联"""
        new_tag = "兹定于合并标签X"
        create = await auth_client_a.post(
            "/api/blogs/add",
            json={"title": "混合标签测试", "content": "正文", "tag_ids": [1], "tag_names": [new_tag]},
        )
        assert create.status_code == 200
        blog_id = create.json()["data"]["id"]
        detail = await auth_client_a.get(f"/api/blogs/detail?id={blog_id}")
        tags_name = detail.json()["data"]["tags_name"]
        assert len(tags_name) == 2  # 默认标签(Python/id=1) + 新标签
        assert new_tag in tags_name