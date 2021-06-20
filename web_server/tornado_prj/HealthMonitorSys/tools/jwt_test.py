from datetime import datetime

import jwt
from HealthMonitor.settings import settings

current_time = datetime.utcnow()

data = jwt.encode({
    "id": 1,
    "nick_name": "taylen",
    "exp": current_time
}, settings["secret_key"]).decode("utf8")
print(data)
import time

time.sleep(2)
# leeway=1 代表1秒过期
data = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwibmlja19uYW1lIjoidGF5bGVuIiwidGVsIjoiMTgzODAzMjkzNDciLCJleHAiOjE2MDkxMzE4MjV9.rnsEyXwMH0blBgxVDYpoj2KHpMd6V6ocNT_T2ckskCw"
send_data = jwt.decode(data, settings["secret_key"], leeway=1, options={"verify_exp": False})  # 类型为dict

print(send_data)
