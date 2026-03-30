from langchain_community.llms.tongyi import Tongyi
# 不用qwen3-max,因为qwen3-max是聊天模型,qwen-max是大语言模型
model = Tongyi(model="qwen-max")

# 调用invoke向模型提问
res = model.invoke(input="我一位女网友叫'张芊薏',请分析这个名字")

print(res)