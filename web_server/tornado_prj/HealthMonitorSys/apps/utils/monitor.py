import redis
import time


def read_from_serial(loop, msg_callback):
    # redis_cli = redis.StrictRedis(**settings["redis"])
    while True:
        time.sleep(0.1)
        data = "new data"
        loop.add_callback(msg_callback)


# def sendtoWsCli(message="{}"):
#     if message != "":
#         s = message.decode()
#         send(s)
