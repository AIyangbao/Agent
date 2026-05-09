import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

completion = client.chat.completions.create(
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "你是位星穹铁道开服牢玩家，你印象最深的游戏剧情是崩铁匹诺康尼区域的剧情"},
        {"role": "user", "content": "你认识流萤吗？星穹铁道那位角色，我是她厨子"},
    ]
)
print(completion.choices[0])
