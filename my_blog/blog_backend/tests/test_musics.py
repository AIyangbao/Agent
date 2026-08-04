"""
音乐模块测试: 公开列表接口
运行: pytest tests/test_musics.py -v
"""
import pytest
from httpx import AsyncClient

class TestMusicList:
    async def test_list_music_success(self, client: AsyncClient):
        """获取音乐列表 -> 200 + data 是list"""
        resp = await client.get("/api/music/list")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert isinstance(data["data"],list)

    async def test_list_music_music_fields(self, client: AsyncClient):
        """列表元素应包含 id/title/artist/src 字段(库里有种子数据时校验)"""
        resp = await  client.get("/api/music/list")
        rows = resp.json()["data"]
        assert isinstance(rows, list)
        if rows: # 空表则不强制字段断言
            row = rows[0]
            for key in ("id", "title", "artist", "src"):
                assert key in row, f"音乐项缺少字段{key}"
            assert isinstance(row["id"], int)