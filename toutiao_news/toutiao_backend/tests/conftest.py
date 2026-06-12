import sys
import os

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取上级目录
parent_dir = os.path.dirname(current_dir)
# 把上级目录插入到搜索路径的最前面
sys.path.insert(0,parent_dir)