"""
博客模块测试:列表、详情、CRUD、权限校验、参数验证
运行:pytest tests/test_blogs.py -v
"""

import pytest
from httpx import AsyncClient

class TestBlogList:
    """博客读取接口测试"""

    async def test_list_blogs(self,client: AsyncClient):
        """获取博客列表 -> 200 + list和 total字段存在"""
        resp = await client.get("/api/blogs/list_blogs?page=1&pageSize=10")
        assert resp.status_code == 200
        data = resp.json()
        assert "list" in data["data"]
        assert "total" in data["data"]
        # 空表时list应为空数组,total应为0或>= 0
        assert isinstance(data["data"]["list"],list)
    
    async def test_get_detail_not_found(self,client: AsyncClient):
        """获取不存在的文章 -> 404"""
        resp = await client.get("/api/blogs/detail?id=99999")
        assert resp.status_code == 404
    
    async def test_add_blog_unauthenticated(self,client: AsyncClient):
        """未登录发文章 -> 401"""
        resp = await client.post(
            "/api/blogs/add",
            json={"title":"未登录发文章","content":"应该被拦截"},
        )
        assert resp.status_code == 401
    async def test_delete_unauthenticated(self,client: AsyncClient):
        """未登录删除文章 -> 401"""
        resp = await client.delete("/api/blogs/delete?id=1")
        assert resp.status_code == 401

class TestBlogCRUD:
    """博客增删改查完整流程(需要登录态)"""
    async def test_add_blog_success(self,auth_client_a: AsyncClient):
        """登录后发文章 -> 200 + 文章ID存在"""
        resp = await auth_client_a.post(
          "/api/blogs/add",
          json={"title":"我的第一篇测试文章","content":"这是内容","tag_ids":[1]}, 
        )
        assert resp.status_code == 200
        blog_data = resp.json()["data"]
        # 如果 add 接口返回的是 BlogResponse 对象，可以进一步断言
        if blog_data:
            assert blog_data.get("title") == "我的第一篇测试文章"
            # 检查标签是否关联成功
            assert blog_data.get("tags_name")
    
    async def test_get_detail_success(self,auth_client_a: AsyncClient):
        """发文章后能获取详情 -> 200"""
        # 先发一篇
        create_resp = await auth_client_a.post(
            "/api/blogs/add",
            json={"title":"详情测试文章","content":"正文内容","tag_ids":[2]},
        )
        assert create_resp.status_code == 200
        blog_id = create_resp.json()["data"]["id"] if create_resp.json().get("data") else None
        if not blog_id:
            # 如果返回结构里没有id,从列表里拿最新的
            list_resp = await auth_client_a.get("/api/blogs/list_blogs?page=1&pageSize=10")
            blog_id = list_resp.json()["data"]["list"][0]["id"]

        # 获取详情
        detail_resp = await auth_client_a.get(f"/api/blogs/detail?id={blog_id}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["data"]["title"] == "详情测试文章"

class TestBlogPermission:
    """博客权限校验测试"""

    async def test_delete_own_blog(self,auth_client_a: AsyncClient):
        """删除自己的文章 -> 200"""
        # 发一篇
        resp = await auth_client_a.post(
            "/api/blogs/add",
            json={"title":"我要删的文章","content":"待删除"},
        )
        assert resp.status_code == 200
        blog_id = resp.json()["data"]["id"]

        # 删除自己的文章
        del_resp = await auth_client_a.delete(f"/api/blogs/delete?id={blog_id}")
        assert del_resp.status_code == 200
    
    async def test_delete_others_blog(self,auth_client_a:AsyncClient,auth_client_b:AsyncClient):
        """用B的身份删除A的文章 -> 403"""
        # A 发一篇文章
        resp = await auth_client_a.post(
            "/api/blogs/add",
            json={"title":"A的文章","content":"B不能删这个"},
        )
        assert resp.status_code == 200
        blog_id = resp.json()["data"]["id"]

        # B 试图删除A的文章
        del_resp = await auth_client_b.delete(f"/api/blogs/delete?id={blog_id}")
        assert del_resp.status_code == 403

class TestBlogValidation:
    """参数验证测试(Pydantic校验)"""
    
    async def test_add_blog_empty_title(self,auth_client_a: AsyncClient):
        """空标题发文章 -> 422(Pydantic 验证失败)"""
        resp = await auth_client_a.post(
            "/api/blogs/add",
            json={"title":"","content":"标题为空应该报错"},
        )
        assert resp.status_code == 422
    
    async def test_add_blog_no_content(self,auth_client_a: AsyncClient):
        """不发 content字段 -> 422"""
        resp = await auth_client_a.post(
            "/api/blogs/add",
            json={"title":"只有标题没有内容"},
        )
        assert resp.status_code == 422