"""Tool 注册表 -- 集中管理所有Tool,加新Tool只需在这里注册"""

from tools.base import BaseTool,ToolDefinition

class ToolRegistry:
    """单例注册表"""

    _tools: dict[str,BaseTool] = {}

    @classmethod
    def register(cls,tool:BaseTool) -> None:
        """注册一个Tool"""
        name = tool.definition().name
        cls._tools[name] = tool

    @classmethod
    def get_all(cls) -> list[BaseTool]:
        """获取所有已注册的Tool实例"""
        return list(cls._tools.values())

    @classmethod
    def get(cls,name: str) -> BaseTool | None:
        """按名称取 Tool"""
        return cls._tools.get(name)

# ========= 注册所有Tool =========
from tools.weather import WeatherTool
from tools.blog_tools import ListTagsTool, RecentBlogsTool
ToolRegistry.register(WeatherTool())
ToolRegistry.register(RecentBlogsTool())