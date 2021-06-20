import time
import redis

redis_cli = None  # redis 客户端

if __name__ == '__main__':
    redis_cli = redis.Redis()
    device_id = "2012290002"
    while 1:
        redis_cli.publish(device_id + "_" + "ecg", 22)
        time.sleep(0.1)