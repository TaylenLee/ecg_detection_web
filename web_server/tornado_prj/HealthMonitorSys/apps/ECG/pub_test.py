import time
import redis
import json

redis_cli = None  # redis 客户端

if __name__ == '__main__':
    redis_cli = redis.Redis()
    device_id = "2012290001"
    n = 0
    m = 0
    while n >= 0:
        res = {"device_no": "2012290001", "ecg": n/100}
        res = json.dumps(res)
        redis_cli.publish(device_id + "_" + "ecg", res)
        print(res)
        n = n + 1
        m = m + 1
        if m == 25:
            m = 0
            time.sleep(0.1)
