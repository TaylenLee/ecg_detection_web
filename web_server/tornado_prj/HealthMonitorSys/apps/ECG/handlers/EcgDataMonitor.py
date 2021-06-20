'''
使用sockjs.tornado实现websocket
'''
import json
from HealthMonitor.handler import RedisHandler
from apps.utils.hdm_decorators import authenticated_async
from HealthMonitor.settings import settings
from datetime import date
import redis
import time
from sockjs.tornado import SockJSConnection

import threading
import multiprocessing


class MonitorHandler(RedisHandler):
    """获取设备序列号"""

    @authenticated_async
    async def get(self, *args, **kwargs):
        re_data = {
            "device_no": self.current_user.device_no
        }
        # print(self.current_user.device_no)
        self.finish(re_data)


class GetEcgDataHandler(RedisHandler):
    """实时订阅心电数据"""

    @authenticated_async
    async def get(self, *args, **kwargs):
        device_no = self.current_user.device_no
        while device_no == "":
            pass
            time.sleep(0.1)


class EcgRealTimeHandler(SockJSConnection):
    # 定义一个连接池，所有客户端的一个集合
    waiters = set()  # 集合元素不重复的对象
    sub_waiters = set()  # 集合元素不重复的对象
    redis_cli = redis.StrictRedis(**settings["redis"])

    def __init__(self, *args, **kwargs):
        self.stop_event = multiprocessing.Event()
        self._consumer = None
        self.device_no = ""
        super(EcgRealTimeHandler, self).__init__(*args, **kwargs)

    # 1.建立连接
    def on_open(self, request):
        # type(self).waiters.add(self)
        pass
        # self.stop_event = multiprocessing.Event()
        # self._consumer = None
        # self.device_no = ""
        # try:
        #     self.waiters.add(self)
        # except Exception as e:
        #     print(e)
        # self._consumer.start()

    # 2.发送消息
    def on_message(self, message):
        try:
            data = {}
            # m = Monitor()
            # data = dict()
            # if message == "system":
            #     data = dict(
            #         mem=m.mem(),
            #         swap=m.swap(),
            #         cpu=m.cpu(),
            #         disk=m.disk(),
            #         net=m.net(),
            #         dt=m.dt()
            #     )
            # # 对消息进行处理，把新的消息推送到所有连接的客户端
            '''
            t_json = None
            try:
                t_json = json.loads(message)
                # print(t_json)
            except:
                t_json = {}
            device_no = t_json.get("device_no", "0000000000")
            if device_no != "0000000000":
                self.device_no = device_no
                print(self.device_no)
            '''
            if self.device_no == "":
                t_json = None
                try:
                    t_json = json.loads(message)
                    # print(t_json)
                except:
                    t_json = {}
                device_no = t_json.get("device_no", "")
                self.device_no = device_no
                type(self).waiters.add(self)
                print(self.device_no)
                # that = self
                # q = multiprocessing.Manager().Queue()
                # q.put(that)
                # pool = multiprocessing.Pool()
                # self._consumer = pool.apply_async(run_proc, args=(q,))
                # self._consumer = multiprocessing.Process(target=run_proc, args=(q,))
                # self._consumer = multiprocessing.Process(target=sayhello)
                # self._consumer = multiprocessing.Process(target=print_deviceinfo, args=(self,))
                # self._consumer.start()

            if message == "system":
                data = {
                    "user": self.redis_cli.get("user")
                }
                # self.broadcast(self.waiters, self.redis_cli.get("18380329347_1251"))  # 广播
                # self.broadcast(self.waiters, message)  # 广播
                self.send("get")
        except Exception as e:
            print(e)

    # 3.关闭连接
    def on_close(self):
        self.stop_event.set()
        print("连接断开")

    @classmethod
    def send_message(cls):
        for client in cls.sub_waiters:
            # client.send(client.device_no)
            # # if client.device_no != "":
            # while client.device_no == "":
            #     pass
            #     time.sleep(0.1)
            # try:
            #     ps = cls.redis_cli.pubsub()
            #     ps.subscribe(client.device_no + "_" + "ecg")
            #     for item in ps.listen():
            #         if item['type'] == 'message':
            #             msg = item['data']
            #             if msg != "":
            #                 s = msg.decode()
            #                 client.send(s)
            # except Exception as e:
            #     print(e)
            try:
                ps = cls.redis_cli.pubsub()
                ps.subscribe(client.device_no + "_" + "ecg")
                for item in ps.listen():
                    if item['type'] == 'message':
                        msg = item['data']
                        if msg != "":
                            s = msg.decode()
                            client.send(s)
                            # print("send data")
            except Exception as e:
                print(e)
        cls.sub_waiters.clear()

    @classmethod
    def pro_send_message(cls, msg):
        for client in cls.waiters:
            client.send(msg)

    @classmethod
    def th_send_message(cls):
        print("back")

'''
def read_from_serial(loop, msg_callback):
    # redis_cli = redis.StrictRedis(**settings["redis"])
    # EcgRealTimeHandler.waiters
    while True:
        time.sleep(0.1)
        if len(EcgRealTimeHandler.waiters) > 0:
            try:
                for client in EcgRealTimeHandler.waiters:
                    EcgRealTimeHandler.sub_waiters.add(client)
                EcgRealTimeHandler.waiters.clear()
                loop.add_callback(msg_callback)
            except Exception as e:
                print(e)
    # loop.add_callback(msg_callback)

'''
def read_from_serial(loop, msg_callback):
    # EcgRealTimeHandler.waiters
    while True:
        time.sleep(0.1)
        if len(EcgRealTimeHandler.waiters) > 0:
            for client in EcgRealTimeHandler.waiters:
                try:
                    redis_cli = redis.StrictRedis(**settings["redis"])
                    ps = redis_cli.pubsub()
                    ps.subscribe(client.device_no + "_" + "ecg")
                    loop.add_callback(msg_callback)
                    for item in ps.listen():
                        if item['type'] == 'message':
                            msg = item['data']
                            if msg != "":
                                s = msg.decode()
                                client.send(s)
                                loop.add_callback(msg_callback)
                except Exception as e:
                    print(e)


def sayhello():
    print("hello world")
    redis_cli = redis.StrictRedis(**settings["redis"])
    ps = redis_cli.pubsub()

    # 订阅topic
    ps.subscribe("2012290001_ecg")
    for item in ps.listen():
        if item['type'] == 'message':
            msg = item['data']
            if msg != "":
                s = msg.decode()
                # for client in EcgRealTimeHandler.waiters:
                #     client.send(s)
                EcgRealTimeHandler.pro_send_message(s)


def run_proc(q):
    print("子进程")
    redis_cli = redis.StrictRedis(**settings["redis"])
    ps = redis_cli.pubsub()

    # 订阅topic
    ps.subscribe(q.get().device_no + "_" + "ecg")
    if not q.get().stop_event.is_set():
        for item in ps.listen():
            if item['type'] == 'message':
                msg = item['data']
                if msg != "":
                    s = msg.decode()
                    q.get().send(s)
            if q.get().stop_event.is_set():
                ps.close()


def print_deviceinfo(obj):
    print(obj.device_no)
