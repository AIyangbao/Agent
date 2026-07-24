# 从零搭建博客 AI Agent：LangChain + DeepSeek + ReAct 架构实践

> 本文记录了为「技术宅小窝」博客系统从零设计并实现 AI 对话助手的完整过程，涵盖分层架构设计、ReAct 循环实现、Tool 工具系统、以及踩过的坑。

## 一、背景

博客系统技术栈：**Vue 3 + FastAPI + MySQL + Docker**，已部署上线。现在要加一个 AI 对话页面，要求：

1. 能进行多轮对话
2. 能调用外部工具（如天气查询）
3. 架构可扩展，以后加新工具不动核心代码
4. 模型可替换（Qwen / DeepSeek / OpenAI）

最终选择 **LangChain + DeepSeek-V4-Flash + ReAct 循环**方案，采用三层解耦架构。

## 二、架构总览

```
┌─────────────────────────────────────────────┐
│                   前端 Vue3                   │
│            AIChat.vue + ai.js                │
└──────────────────┬──────────────────────────┘
                   │ POST /api/ai/chat
                   ▼
┌─────────────────────────────────────────────┐
│                 API 层 (routers/)             │
│          JWT 认证 → 请求校验 → 响应封装         │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│              Service 层 (services/)           │
│         AgentService — ReAct 循环核心          │
│    Think → Act → Observe → Think → Answer    │
└──────┬───────────────────────┬──────────────┘
       │                       │
       ▼                       ▼
┌──────────────┐     ┌──────────────────────┐
│  LLM 层      │     │     Tool 层           │
│ (llm/)       │     │  (tools/)             │
│              │     │                       │
│ BaseLLM      │     │ BaseTool              │
│   ↕          │     │ ToolRegistry          │
│ QwenLLM      │     │ WeatherTool           │
│   ↕          │     │   ...可扩展           │
│ Factory      │     │                       │
└──────────────┘     └──────────────────────┘
```

**设计原则：三层解耦，各司其职**

| 层 | 职责 | 关键文件 |
|---|------|---------|
| Tool 层 | 定义工具接口，注册管理 | `tools/base.py`, `tools/registry.py`, `tools/weather.py` |
| LLM 层 | 封装大模型调用，支持工厂切换 | `llm/base.py`, `llm/qwen.py`, `llm/factory.py` |
| Service 层 | ReAct 循环，串联 LLM 与 Tool | `services/agent_service.py` |
| API 层 | FastAPI 路由，JWT 认证 | `routers/ai.py`, `schemas/ai.py` |

## 三、Tool 层：工具系统设计

### 3.1 抽象基类

所有工具继承 `BaseTool`，必须实现两个方法：`definition()` 给 LLM 看的工具描述，`execute()` 实际执行逻辑。

```python
# tools/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel

class ToolDefinition(BaseModel):
    """工具的元信息（给 LLM 看的）"""
    name: str
    description: str
    parameters: dict  # JSON Schema 格式

class BaseTool(ABC):
    """所有 Tool 必须继承此类"""

    @abstractmethod
    def definition(self) -> ToolDefinition:
        """返回给 LLM 看的工具定义"""

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """实际执行工具，返回字符串结果"""
```

### 3.2 注册表（单例模式）

集中管理所有工具，加新工具只需在这里 `register` 一行：

```python
# tools/registry.py
class ToolRegistry:
    """单例注册表"""
    _tools: dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool) -> None:
        name = tool.definition().name
        cls._tools[name] = tool

    @classmethod
    def get_all(cls) -> list[BaseTool]:
        return list(cls._tools.values())

    @classmethod
    def get(cls, name: str) -> BaseTool | None:
        return cls._tools.get(name)

# ========= 注册所有 Tool =========
from tools.weather import WeatherTool
ToolRegistry.register(WeatherTool())
```

### 3.3 天气工具实现

复用已有的 `dify_work_api` 微服务（端口 8081）作为天气数据源：

```python
# tools/weather.py
import httpx
from tools.base import BaseTool, ToolDefinition

class WeatherTool(BaseTool):
    """查询指定城市的天气"""

    _DIFY_URL = "http://localhost:8081/weather"
    _DIFY_TOKEN = "itcast"
    _TIMEOUT = 10

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_weather",
            description="查询指定城市的天气，支持全国主要城市。参数 city 为中文城市名",
            parameters={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "中文城市名称，如北京、上海、广州、深圳"
                    }
                },
                "required": ["city"]
            }
        )

    async def execute(self, city: str = "") -> str:
        try:
            async with httpx.AsyncClient(timeout=self._TIMEOUT) as client:
                resp = await client.post(
                    self._DIFY_URL,
                    json={"location": city.strip()},
                    headers={"Authorization": f"Bearer {self._DIFY_TOKEN}"}
                )
                if resp.status_code == 403:
                    return "天气服务认证失败"
                data = resp.json()
                return str(data) if not isinstance(data, dict) \
                    else data.get("message", str(data))
        except httpx.TimeoutException:
            return "天气查询超时，请稍后再试"
        except httpx.ConnectError:
            return "天气服务未启动"
        except Exception as e:
            return f"天气查询异常: {e}"
```

**加新 Tool 只需 3 步：**
1. 新建 `tools/xxx.py`，继承 `BaseTool`
2. 实现 `definition()` 和 `execute()`
3. 在 `registry.py` 末尾加一行 `ToolRegistry.register(XxxTool())`

## 四、LLM 层：模型封装与工厂模式

### 4.1 抽象接口

```python
# llm/base.py
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def invoke(self, messages: list, tools: list[dict] | None = None) -> Any:
        """
        调用 LLM
        - messages: LangChain 消息列表
        - tools: 可选，函数调用 schema
        - 返回: LangChain AIMessage
        """
```

### 4.2 千问/DeepSeek 实现

通过 LangChain 的 `ChatTongyi` 封装（百炼平台的 DeepSeek 模型也走 DashScope API）：

```python
# llm/qwen.py
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import BaseMessage
from llm.base import BaseLLM

class QwenLLM(BaseLLM):
    """封装 ChatTongyi，支持 function calling"""

    def __init__(self, model: str = 'qwen-plus', api_key: str = ""):
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY 未设置")
        self._llm = ChatTongyi(
            model=model,
            dashscope_api_key=api_key,
            temperature=0.7,
        )

    def invoke(self, messages: list[BaseMessage], tools: list[dict] | None = None):
        llm = self._llm
        if tools:
            llm = llm.bind_tools(tools)  # 绑定工具，启用 function calling
        return llm.invoke(messages)
```

### 4.3 工厂函数

从配置读取参数，调用方不关心具体实现：

```python
# llm/factory.py
from config.settings import settings
from llm.qwen import QwenLLM

def get_llm() -> QwenLLM:
    if not settings.DASHSCOPE_API_KEY:
        raise RuntimeError("DASHSCOPE_API_KEY 未配置")
    return QwenLLM(
        model=settings.QWEN_MODEL or "qwen-plus",
        api_key=settings.DASHSCOPE_API_KEY,
    )
```

**想换模型？** 只需新建 `llm/deepseek.py`，实现 `BaseLLM`，然后在 `factory.py` 改一行 `return DeepSeekLLM(...)`。

## 五、Service 层：ReAct 循环核心

这是整个 Agent 的大脑，实现 **ReAct（Reasoning + Acting）** 循环：

```
用户提问 → LLM 思考 → 需要工具吗？
                          ├─ 是 → 调用工具 → 拿到结果 → 回到 LLM 思考
                          └─ 否 → 直接回答
```

### 5.1 完整代码

```python
# services/agent_service.py
from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage, ToolMessage
)
from tools.registry import ToolRegistry
from llm.factory import get_llm

SYSTEM_PROMPT = """你是[技术宅小窝]博客的AI助手。你可以使用工具来帮助用户。

规则:
1. 技术问题直接回答，需要代码时给出代码示例
2. 需要实时数据(如天气)时，调用对应工具
3. 回答简洁、准确
"""

class AgentService:
    """无状态 Agent —— 每次请求创建一个实例"""
    MAX_ITERATIONS = 5  # 防止死循环

    def __init__(self):
        self._llm = get_llm()
        self._tools = ToolRegistry.get_all()
        self._tool_map = {t.definition().name: t for t in self._tools}

    def _build_tool_schemas(self) -> list[dict]:
        """构建 LangChain 格式的 tool schema"""
        schemas = []
        for t in self._tools:
            d = t.definition()
            schemas.append({
                "type": "function",
                "function": {
                    "name": d.name,
                    "description": d.description,
                    "parameters": d.parameters,
                }
            })
        return schemas

    async def chat(self, message: str, history: list[dict] | None = None) -> str:
        """处理一次对话"""
        messages = self._build_messages(message, history or [])
        tool_schemas = self._build_tool_schemas()

        for _ in range(self.MAX_ITERATIONS):
            # Think: LLM 决定是回答还是调用工具
            response = self._llm.invoke(messages, tools=tool_schemas or None)

            # 没有工具调用 → 直接返回回答
            if not hasattr(response, "tool_calls") or not response.tool_calls:
                return response.content

            # Act: 执行 LLM 要求调用的工具
            messages.append(response)
            for tc in response.tool_calls:
                tool_name = tc["name"]
                tool_args = tc["args"]
                tool = self._tool_map.get(tool_name)

                if tool:
                    result = await tool.execute(**tool_args)
                else:
                    result = f"未知工具: {tool_name}"

                # Observe: 把工具结果喂回给 LLM
                messages.append(ToolMessage(
                    content=result,
                    tool_call_id=tc["id"]
                ))
        return "抱歉，处理超时，请简化问题后重试"

    def _build_messages(self, message: str, history: list[dict]) -> list:
        """构建消息链：System + 历史对话 + 当前问题"""
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for h in history[-10:]:  # 最多保留 10 轮历史
            if h.get("role") == "user":
                messages.append(HumanMessage(content=h["content"]))
            elif h.get("role") == "ai":
                messages.append(AIMessage(content=h["content"]))
        messages.append(HumanMessage(content=message))
        return messages
```

### 5.2 ReAct 循环流程图

```
┌─────────────┐
│   用户消息    │
└──────┬──────┘
       ▼
┌─────────────────────────────────┐
│  构建 messages 链                │
│  SystemPrompt + History + Input │
└──────────────┬──────────────────┘
               ▼
        ┌──────────────┐
        │  LLM.invoke() │ ◄──── tools schema
        └──────┬───────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
  有 tool_calls？      没有
      │                 │
      ▼                 ▼
┌───────────┐    ┌───────────┐
│ 执行工具   │    │  返回回答   │
│ execute() │    │  response  │
└─────┬─────┘    └───────────┘
      │
      ▼
┌───────────────────┐
│ ToolMessage 回传    │
│ 加入 messages 链    │
└─────────┬─────────┘
          │
          ▼
    回到 LLM.invoke()  ◄── 循环（最多 5 次）
```

## 六、API 层：路由与认证

### 6.1 请求/响应模型

```python
# schemas/ai.py
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: list[dict] = Field(default_factory=list)

class ChatReply(BaseModel):
    reply: str
```

### 6.2 路由

```python
# routers/ai.py
from fastapi import APIRouter, Depends
from schemas.ai import ChatRequest
from services.agent_service import AgentService
from utils.auth import get_current_user
from utils.response import success_response, error_response

router = APIRouter(prefix="/api/ai", tags=["ai"])

@router.post("/chat")
async def chat(
    req: ChatRequest,
    current_user: dict = Depends(get_current_user),  # JWT 认证
):
    try:
        agent = AgentService()
        reply = await agent.chat(req.message, req.history)
        return success_response(data={"reply": reply})
    except RuntimeError as e:
        return error_response(code=503, message=str(e))
    except Exception as e:
        return error_response(code=500, message=str(e))
```

## 七、前端对接

### 7.1 API 封装

```javascript
// src/api/ai.js
import { post } from './request'

export function chatWithAI(message, history = []) {
  return post('/ai/chat', { message, history })
}
```

### 7.2 对话页面核心逻辑

```javascript
// AIChat.vue —— 发送消息
async function sendMessage(text) {
  const msg = (text || input.value).trim()
  if (!msg || loading.value) return

  messages.value.push({ role: 'user', content: msg })
  loading.value = true

  try {
    // 带上历史对话，实现多轮上下文
    const history = messages.value.slice(0, -1).map(m => ({
      role: m.role,
      content: m.content
    }))
    const res = await chatWithAI(msg, history)
    messages.value.push({ role: 'assistant', content: res.reply })
    apiOnline.value = true
  } catch (e) {
    // 后端不可用 → 降级到演示模式
    apiOnline.value = false
    messages.value.push({ role: 'assistant', content: getMockReply(msg) })
  } finally {
    loading.value = false
  }
}
```

### 7.3 Token 同步问题

踩了一个坑：Pinia store 的 `login()` 只存了用户名，没存 token。但 `request.js` 从 `localStorage` 读 `blog_token`，导致 AI 请求不带 token → 后端返回 401 → 前端降级到演示模式。

修复方案：`login()` 同时接收 token 并存入 store + localStorage：

```javascript
// store/index.js
function login(name, accessToken) {
  username.value = name
  token.value = accessToken
  localStorage.setItem('blog_user', name)
  localStorage.setItem('blog_token', accessToken)
}
```

## 八、配置

```ini
# .env
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx
QWEN_MODEL=deepseek-v4-flash
```

```python
# config/settings.py
class Settings(BaseSettings):
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    QWEN_MODEL: str = os.getenv("QWEN_MODEL", "qwen-plus")
```

## 九、踩坑记录

### 坑 1：模型名不兼容

| 模型名 | 结果 | 原因 |
|--------|------|------|
| `qwen-plus` | ❌ 403 免费额度耗尽 | 免费额度是账号级别的，换 Key 没用 |
| `qwen3.7-plus` | ❌ url error | LangChain `ChatTongyi` 不认识这个模型名 |
| `deepseek-v4-flash` | ✅ 正常 | 走百炼平台 DashScope API，有 100 万免费额度 |

**教训**：百炼控制台显示的模型名不一定等于 LangChain 可用的模型名，需要实际测试。

### 坑 2：免费额度是账号级别的

重新生成 API Key 不能解决额度问题——免费额度绑定的是阿里云账号，不是 Key。需要在百炼控制台关闭「仅使用免费额度」开关，走按量付费。

### 坑 3：前后端 Token 不同步

前端 store 和 localStorage 的 token 存储不同步，导致带不上 Authorization header。解决方案见第七章。

### 坑 4：LangChain 版本兼容性

`langchain-community` 已标记为 sunset（停止维护），未来需迁移到独立集成包（如 `langchain-tongyi`）。当前版本仍可用：

```
langchain==1.3.13
langchain-community==0.4.2
langchain-core==1.4.9
dashscope==1.26.3
```

## 十、目录结构

```
blog_backend/
├── tools/
│   ├── __init__.py
│   ├── base.py              # BaseTool 抽象类 + ToolDefinition
│   ├── registry.py          # ToolRegistry 单例注册表
│   └── weather.py           # 天气查询工具
├── llm/
│   ├── __init__.py
│   ├── base.py              # BaseLLM 抽象类
│   ├── qwen.py              # QwenLLM（ChatTongyi 封装）
│   └── factory.py           # get_llm() 工厂函数
├── services/
│   ├── __init__.py
│   └── agent_service.py     # AgentService ReAct 循环
├── routers/
│   └── ai.py                # POST /api/ai/chat
├── schemas/
│   └── ai.py                # ChatRequest / ChatReply
├── config/
│   └── settings.py          # DASHSCOPE_API_KEY + QWEN_MODEL
└── .env                     # 环境变量
```

## 十一、扩展指南

### 加一个新工具（如「搜索博客」）

**Step 1**：新建 `tools/blog_search.py`

```python
from tools.base import BaseTool, ToolDefinition

class BlogSearchTool(BaseTool):
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="search_blog",
            description="在博客中搜索文章",
            parameters={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词"
                    }
                },
                "required": ["keyword"]
            }
        )

    async def execute(self, keyword: str = "") -> str:
        # 调用博客搜索 API
        # 返回搜索结果字符串
        return f"找到以下与「{keyword}」相关的文章：..."
```

**Step 2**：在 `registry.py` 注册

```python
from tools.blog_search import BlogSearchTool
ToolRegistry.register(BlogSearchTool())
```

**完成。** 不需要改 Agent 核心代码，LLM 会自动发现新工具并决定何时调用。

### 换一个模型

**Step 1**：新建 `llm/openai.py`，继承 `BaseLLM`

**Step 2**：在 `factory.py` 改一行：

```python
def get_llm() -> BaseLLM:
    return OpenAILLM(model="gpt-4o", api_key=settings.OPENAI_API_KEY)
```

## 十二、总结

整个 Agent 架构的核心思路就三个词：**抽象、注册、循环**。

- **抽象**：`BaseTool` 和 `BaseLLM` 定义统一接口，具体实现可替换
- **注册**：`ToolRegistry` 集中管理工具，加新工具一行代码
- **循环**：`AgentService` 的 ReAct 循环串联一切，Think → Act → Observe → Answer

这不是什么高深的架构，但通过分层解耦，每一层都可以独立修改、独立测试。对于一个个人博客项目来说，这个架构在「够用」和「可扩展」之间找到了平衡点。

---

*项目地址：[GitHub](https://github.com/AIyangbao/Agent) | 线上体验：[blog.fireflyai.site](https://blog.fireflyai.site)*
