'''
使用tornado.websocket实现websocket
'''

import json
from HealthMonitor.handler import RedisHandler
from apps.utils.hdm_decorators import authenticated_async
from HealthMonitor.settings import settings
from tornado.websocket import WebSocketHandler
from datetime import date
import redis
import time

import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor


class MonitorHandler(RedisHandler):
    """获取设备序列号"""

    @authenticated_async
    async def get(self, *args, **kwargs):
        re_data = {
            "device_no": self.current_user.device_no
        }
        # print(self.current_user.device_no)
        self.finish(re_data)


class Consumer(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        redis_cli = redis.StrictRedis(**settings["redis"])
        ps = redis_cli.pubsub()
        ps.subscribe("2012290001_ecg")
        if not self.stop_event.is_set():
            for item in ps.listen():
                if item['type'] == 'message':
                    msg = item['data']
                    if msg != "":
                        s = msg.decode()
                        RealTimeHandler.send_message(s)
                if self.stop_event.is_set():
                    ps.close()


class ThreadConsumer(threading.Thread):
    daemon = True

    def __init__(self, kafka_consumer):
        super(ThreadConsumer, self).__init__()

    def run(self):
        redis_cli = redis.StrictRedis(**settings["redis"])
        ps = redis_cli.pubsub()
        ps.subscribe("2012290001_ecg")
        for item in ps.listen():
            if item['type'] == 'message':
                msg = item['data']
                if msg != "":
                    s = msg.decode()
                    RealTimeHandler.send_message(s)


class RealTimeHandler(WebSocketHandler):
    users = set()
    # executor = ThreadPoolExecutor(20)

    def __init__(self, *args, **kwargs):
        # self.stop_event = multiprocessing.Event()
        # self._consumer = Consumer()
        # self._tconsumer = ThreadConsumer()
        self.device_no = ""
        super(RealTimeHandler, self).__init__(*args, **kwargs)

    def open(self, *args):
        self.set_nodelay(True)
        if not self.device_no == "":
            type(self).user.add(self)

    def on_message(self, message):
        if self.device_no == "":
            t_json = None
            try:
                t_json = json.loads(message)
                # print(t_json)
            except:
                t_json = {}
            device_no = t_json.get("device_no", "")
            self.device_no = device_no
            print(self.device_no)
            self.users.add(self)
            # t0 = multiprocessing.Process(target=receive, args=(self.users, ))
            # t0.setDaemon(True)
            # t0.join()
            # t0.start()
            # self.receive()

            # self._tconsumer.start()
            # self._consumer.start()
            # pool = multiprocessing.Pool()
            # self._consumer = pool.apply_async(run_proc, args=(q,))
            # self._consumer = multiprocessing.Process(target=run_proc, args=(q,))
            # self._consumer = multiprocessing.Process(target=sayhello)
            # self._consumer = multiprocessing.Process(target=print_deviceinfo, args=(self,))
            # self._consumer.start()

        # if message == "system":
        #     if not self.device_no == "":
        #         self.write_message(self.device_no)  # 广播

    # self.broadcast(self.waiters, message)  # 广播
    # self.send(self.redis_cli.get("18380329347_1251"))

    def on_close(self):
        # self._consumer.stop()
        self.users.remove(self)
        print("WebSocket closed")

    def check_origin(self, origin):
        return True  # 允许WebSocket的跨域请求

    @classmethod
    def send_message(cls, msg):
        for client in cls.users:
            client.write_message(msg)

    @classmethod
    def thread_send_message(cls):
        while True:
            for client in cls.users:
                redis_cli = redis.StrictRedis(**settings["redis"])
                ps = redis_cli.pubsub()
                ps.subscribe("2012290001_ecg")
                for item in ps.listen():
                    if item['type'] == 'message':
                        msg = item['data']
                        if msg != "":
                            s = msg.decode()
                            client.write_message(s)

    # @run_on_executor
    def receive(self):
        redis_cli = redis.StrictRedis(**settings["redis"])
        ps = redis_cli.pubsub()
        ps.subscribe("2012290001_ecg")
        for item in ps.listen():
            if item['type'] == 'message':
                msg = item['data']
                if msg != "":
                    s = msg.decode()
                    # RealTimeHandler.send_message(s)
                    self.write_message(s)
