"""
用户模块测试:注册、登录、重复注册、密码错误
运行: pytest tests/test_users.py -v
"""

import pytest
from httpx import AsyncClient

class TestUserRegister:
    """用户注册相关测试"""
    
    async def test_register_success(self,client: AsyncClient):
        """正常注册 -> 200 + 返回 token + 用户名正确"""
        resp = await client.post(
            "/api/user/register",
            json={"username": "test_user","password":"test123456"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert data["data"]["access_token"] # token 不为空
        assert data["data"]["username"] == "test_user"
    
    async def test_register_duplicate(self,client: AsyncClient):
        """重复注册同一用户名 -> 400"""
        # 先注册一次
        await client.post(
            "/api/user/register",
            json={"username":"dup_user","password":"test123456"},
        )
        # 在注册同样的用户名
        resp = await client.post(
            "/api/user/register",
            json={"username":"dup_user","password":"test123456"},
        )
        assert resp.status_code == 400

class TestUserLogin:
    """用户登录相关测试"""

    async def test_login_success(self,client: AsyncClient):
        """正常登录 -> 200 + token"""
        # 先注册
        await client.post(
            "/api/user/register",
            json={"username":"login_user","password":"login123456"},
        )
        # 再登录
        resp = await client.post(
            "/api/user/login",
            json={"username":"login_user","password":"login123456"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["access_token"]
    
    async def test_login_wrong_passowrd(self,client:AsyncClient):
        """密码错误 -> 401"""
        await client.post(
            "/api/user/register",
            json={"username":"pwd_user","password":"correct123"},
        )
        resp = await client.post(
            "/api/user/login",
            json={"username":"pwd_user","password":"wrong123"},
        )
        assert resp.status_code == 401
    
    async def test_login_not_exist(self,client: AsyncClient):
        """用户名不存在 -> 401"""
        resp = await client.post(
            "/api/user/login",
            json={"username":"nobody","password":"whatever123"},
        )
        assert resp.status_code == 401
