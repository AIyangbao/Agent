"""Tool 抽象基类 -- 定义统一的Tool接口"""
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel

class ToolDefinition(BaseModel):
    """一个Tool的原信息(name + description + 参数 schema 给LLM看)"""
    name: str
    description: str
    parameters: dict # JSON Schema格式

class BaseTool(ABC):
    """所有Tool 必须继承此类"""

    @abstractmethod
    def definition(self) -> ToolDefinition:
        """返回给LLM看的工具定义"""
    
    @abstractmethod
    async def execute(self,**kwargs) -> str:
        """实际执行工具,返回字符串结果"""