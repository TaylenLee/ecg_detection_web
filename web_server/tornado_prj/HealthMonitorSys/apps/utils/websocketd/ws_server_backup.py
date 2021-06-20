import traceback
import json
import threading
from sys import stdout, stdin
import time
import redis
import MySQLdb

# 不查询历史数据可以不使用mongodb
# import pymongo


# conn = MySQLdb.connect(host='localhost', port=3306, db='health_monitor_sys', user='root', passwd='123456', charset='utf8')
# cur = conn.cursor()

is_quit = 0  # 线程退出标识
device_no = ""  # 设备唯一id
ecgReport_id = ""  # 当前心电数据表所对应的的报告ID
out_time = 60  # 超时时间
redis_cli = None  # redis 客户端
# db_connection = None  # mysql 客户端
# cur = None
start_save_ecg = False  # 是否存储数据到数据库
end_save_ecg = False
ecg_data = []
PUBLISH_NAME = "ecg"


# db_connection = None  # mongodb 客户端
# db = None  # mongodb
# db_ip = "127.0.0.1"
# db_port = 27017


def receive():
    """
            接收数据+
    """
    global device_no
    global ecgReport_id
    global is_quit
    global start_save_ecg
    global end_save_ecg
    global ecg_data
    global out_time
    while 1:
        str_receive = stdin.readline().strip()
        if not str_receive:
            is_quit = 1
            break
        # 处理心跳数据
        if str_receive == "ping":
            out_time = 60
            send("pong")
            continue
        # 处理结束保存数据通知

        if str_receive == "end_save_ecg":
            start_save_ecg = False
            end_save_ecg = True
            '''
            data = {
                "ecgdata": ecg_data
            }
            data = json.dumps(data)
            add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            conn = MySQLdb.connect(host='localhost', port=3306, db='health_monitor_sys', user='root', passwd='123456',
                                   charset='utf8')
            cur = conn.cursor()
            sql = "INSERT INTO ECGDATA(ADD_TIME,ECGREPORT_ID,ECG_DATA) VALUES (%s,%s,%s)"
            param = (add_time, ecgReport_id, data)
            try:
                cur.execute(sql, param)
                conn.commit()
                print("insert ok")
            except:
                # 发生错误时回滚
                conn.rollback()
            ecg_data.clear()
            conn.close()
            '''
            continue

        # 处理数据，数据格式str(json)
        t_json = None
        try:
            t_json = json.loads(str_receive)
        except:
            t_json = {}
        ecgReport_id = t_json.get("ecgReport_id", "")
        if ecgReport_id != "":
            start_save_ecg = True
        else:
            start_save_ecg = False
        device_no = t_json.get("device_no", "")
        if device_no == "":
            is_quit = 1
            break


def wait_redis():
    global redis_cli
    global device_no
    global start_save_ecg
    global ecg_data
    global is_quit
    while device_no == "":
        pass
        time.sleep(0.1)
    try:
        ps = redis_cli.pubsub()
        ps.subscribe(device_no + "_" + PUBLISH_NAME)
        for item in ps.listen():
            if item['type'] == 'message':
                toDo(item['data'])
                if start_save_ecg:
                    ecg_data.append(json.loads(item['data'].decode()).get(PUBLISH_NAME))

    except:
        traceback.print_exc()
        is_quit = 1


# def wait_redis_saveEcgData():
#     global redis_cli
#     global device_no
#     global ecgReport_id
#     global is_quit
#     while device_no == "" or ecgReport_id == "":
#         pass
#         time.sleep(0.1)
#     try:
#         ps = redis_cli.pubsub()
#         ps.subscribe(device_no + "_" + PUBLISH_NAME)
#         for item in ps.listen():
#             if item['type'] == 'message':
#                 toDo(item['data'])
#     except:
#         traceback.print_exc()
#         is_quit = 1

def toDo(message="{}"):
    if message != "":
        s = message.decode()
        send(s)


def send(str_send):
    """
            发送数据
    str_send: str
    """
    str_send = str_send + "\n"
    stdout.write(str_send)
    stdout.flush()


if __name__ == '__main__':
    # 连接数据库
    redis_cli = redis.Redis()

    db_connection = MySQLdb.connect(host="127.0.0.1", port=3306, db='health_monitor_sys', user="root", passwd="123456",
                                    charset='utf8')
    cur = db_connection.cursor()

    # 收消息线程
    t0 = threading.Thread(target=receive)
    t0.setDaemon(True)
    t0.start()
    # 收数据库消息线程
    t1 = threading.Thread(target=wait_redis)
    t1.setDaemon(True)
    t1.start()

    # 主程序循环，接收超时或者主动退出
    # while is_quit == 0:
    #     time.sleep(1)
    #     out_time -= 1
    #     if out_time <= 0:
    #         break
    while True:
        pass
        if end_save_ecg:
            data = {
                "ecgdata": ecg_data
            }
            data = json.dumps(data)
            add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # conn = MySQLdb.connect(host='localhost', port=3306, db='health_monitor_sys', user='root', passwd='123456',
            #                        charset='utf8')
            # cur = conn.cursor()
            sql = "INSERT INTO ECGDATA(ADD_TIME,ECGREPORT_ID,ECG_DATA) VALUES (%s,%s,%s)"
            param = (add_time, ecgReport_id, data)
            try:
                cur.execute(sql, param)
                db_connection.commit()
                print("insert ok")
            except:
                # 发生错误时回滚
                db_connection.rollback()
            ecg_data.clear()
            end_save_ecg = False
            # db_connection.close()

        time.sleep(0.1)

# 一个线程大概20m 4G内存 大概200人，使用gevent补丁可以增大2倍
