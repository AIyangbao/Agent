"""天气查询 Tool -- 复用已有的dify_work_api 微服务"""
import httpx
from tools.base import BaseTool, ToolDefinition

class WeatherTool(BaseTool):
    """查询指定城市的天气(通过 dify_work_api)"""

    _DIFY_URL = "http://localhost:8081/weather"
    _DIFY_TOKEN = "itcast"
    _TIMEOUT = 10

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_weather",
            description="查询指定城市的天气,支持全国主要城市.参数city为中文城市名,如北京、深圳、广州",
            parameters={
                "type": "object",
                "properties":{
                    "city":{
                    "type": "string",
                    "description": "中文城市名称,如北京、上海、广州、深圳"
                }
                },
                "required":["city"]
            }
        )
    async def execute(self, city: str = "") -> str:
        """调用 dify_work_api 获取天气"""
        try:
            async with httpx.AsyncClient(timeout=self._TIMEOUT) as client:
                resp = await client.post(
                    self._DIFY_URL,
                    json={"location": city.strip()},
                    headers={"Authorization":f"Bearer {self._DIFY_TOKEN}"}
                )

                if resp.status_code == 403:
                    return "天气服务认证失败,请联系管理员"
                
                data = resp.json()

                if isinstance(data,dict) and data.get("status") == "error":
                    return data.get("message","天气查询失败")
                
                # dify 返回的直接是自然语言字符串
                return str(data) if not isinstance(data,dict) else data.get("message",str(data))
            
        except httpx.TimeoutException:
          return "天气查询超时,请稍后再试"
        except httpx.ConnectError:
          return "天气服务未启动,请检查 dify_work_api 是否在运行"
        except Exception as e:
            return f"天气查询异常: {e}"