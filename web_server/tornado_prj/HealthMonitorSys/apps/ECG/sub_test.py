import time
import redis


if __name__ == '__main__':
    rc = redis.StrictRedis(host='127.0.0.1', port='6379')
    ps = rc.pubsub()
    ps.subscribe("2012290001_ecg")  # 从liao订阅消息
    for item in ps.listen():  # 监听状态：有消息发布了就拿过来
        if item['type'] == 'message':
            print(item['data'])
            ps
            # ps.close()
    ps.subscribe("2012290002_ecg")  # 从liao订阅消息
    for item in ps.listen():  # 监听状态：有消息发布了就拿过来
        if item['type'] == 'message':
            print(item['data'])
            ps.close()