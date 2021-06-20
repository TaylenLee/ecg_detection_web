import os
import json
# 获取当前文件所在的目录
root_path = os.path.dirname(__file__)

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(root_path)
print(BASE_DIR)


data = {}

data = json.dumps(data)
print(type(data))