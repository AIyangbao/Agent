from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import FewShotPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.tongyi import Tongyi
from langchain_community.chat_models.tongyi import ChatTongyi

template = PromptTemplate.from_template("我的邻居是:{lastname},最喜欢:{hobby}")

res = template.format(lastname="张大明",hobby="钓鱼")
print(res,type(res))

res2 = template.invoke({"lastname":"周杰伦","hobby":"唱歌"})
print(res2,type(res2))