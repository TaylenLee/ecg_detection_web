import traceback
import json
import threading
from sys import stdout, stdin
import time
import redis
# import MySQLdb
from pymysql import *

import numpy as np
from ecgdetectors import Detectors
from hrv import HRV

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
update_hr = False  # 是否实时更新心率值
# end_save_ecg = False
ecg_data = []
fs = 256  # 采样频率
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
    global update_hr
    global fs
    # global end_save_ecg
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
            if update_hr:
                if (len(ecg_data) > fs * 5):
                    detectors = Detectors(fs)
                    r_peaks = detectors.hamilton_detector(ecg_data)
                    hrv = HRV(fs)
                    hr = hrv.HR(r_peaks)
                    hr = hr.tolist()
                    hr.remove(max(hr))
                    hr_avg = round(sum(hr) / len(hr))
                    hear_rate = {
                        "heart_rate": hr_avg
                    }
                    hear_rate = json.dumps(hear_rate)
                    send(hear_rate)
                    del ecg_data[0: 2 * fs]
            continue

        # 收到此通知，则需要实时计算心率传给前端显示
        if str_receive == "start_realtime":
            update_hr = True
            continue

            # if (len(ecg_data) > fs * 5):
            #     detectors = Detectors(fs)
            #     r_peaks = detectors.hamilton_detector(ecg_data)
            #     hrv = HRV(fs)
            #     hr = hrv.HR(r_peaks)
            #     hr = hr.tolist()
            #     hr.remove(max(hr))
            #     hr_avg = round(sum(hr) / len(hr))
            #     hear_rate = {
            #         "heart_rate": hr_avg
            #     }
            #     hear_rate = json.dumps(hear_rate)
            #     send(hear_rate)
            #     del ecg_data[0: fs]
        # 处理结束保存数据通知
        if str_receive == "end_save_ecg" or str_receive == "end_save_ecg_threeMin":
            start_save_ecg = False
            # ecg_signal = np.asarray(ecg_data)
            detectors = Detectors(fs)
            r_peaks = detectors.hamilton_detector(ecg_data)
            hrv = HRV(fs)
            hr = hrv.HR(r_peaks)
            rri = hrv._intervals(r_peaks)
            hr = hr.tolist()
            del hr[0: 3]
            rri = rri.tolist()
            for i in range(0, len(hr)):
                hr[i] = round(hr[i])
            for i in range(0, len(rri)):
                rri[i] = round(rri[i])
            heartRateMax = max(hr)
            heartRateMin = min(hr)
            heartRateAvg = round(sum(hr) / len(hr))
            tachycardia = 0
            bradycardia = 0
            if heartRateMax > 100:
                tachycardia = 1
            if heartRateMin < 60:
                bradycardia = 1
            hrv_parameter = {}
            if str_receive == "end_save_ecg_threeMin":
                sdnn = round(hrv.SDNN(r_peaks), 4)
                rmssd = round(hrv.RMSSD(r_peaks), 4)
                lf_div_hf = round(hrv.fAnalysis(r_peaks), 4)
                lf = round(hrv.lf, 4)
                hf = round(hrv.hf, 4)
                hrv_parameter = {
                    "sdnn": sdnn,
                    "rmssd": rmssd,
                    "lf_div_hf": lf_div_hf,
                    "lf": lf,
                    "hf": hf
                }
            hrv_parameter = json.dumps(hrv_parameter)
            # result = biosppy.signals.ecg.ecg(ecg_signal, sampling_rate=256, show=False)
            # rpeaks = result['rpeaks']
            # hr = result['heart_rate']
            # hr_ts = result['heart_rate_ts']
            # heartRateMax = max(hr)
            # heartRateMin = min(hr)
            # heartRateAvg = round(sum(hr) / len(hr))
            # for i in range(0, len(hr)):
            #     nni[i] = round(hr[i])
            # nni = tools.nn_intervals(rpeaks)  # RR间期
            # for i in range(0, len(nni)):
            #     nni[i] = round(nni[i] / 256.0 * 1000.0)

            data = {
                "ecgdata": ecg_data,
                "hr_data": hr,
                # "hr_ts": hr_ts,
                "rri": rri
            }
            data = json.dumps(data)
            add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # conn = MySQLdb.connect(host='localhost', port=3306, db='health_monitor_sys', user='root', passwd='123456',charset='utf8')
            conn = connect(host='localhost', port=3306, database='health_monitor_sys', user='root', password='123456',
                           charset='utf8')
            cur = conn.cursor()
            # sql = "INSERT INTO ECGDATA(ADD_TIME,ECGREPORT_ID,ECG_DATA) VALUES (%s,%s,%s)"
            # param = (add_time, ecgReport_id, data)
            # sql = "UPDATE ECGTESTREPORTS SET ADD_TIME = %s, HEARTRATEAVG = %s, HEARTRATEMAX = %s, HEARTRATEMIN = %s, ECG_DATA = %s, HRV_PARAMETER = %s WHERE ID = %s"
            sql = "update ecgtestreports set add_time = %s, heartRateAvg = %s, heartRateMax = %s, heartRateMin = %s, tachycardia = %s, bradycardia = %s, ecg_data = %s, hrv_parameter = %s where id = %s"
            param = (add_time, heartRateAvg, heartRateMax, heartRateMin, tachycardia, bradycardia, data, hrv_parameter, ecgReport_id)
            # sql = "UPDATE ECGTESTREPORTS SET ADD_TIME = %s, HEARTRATEAVG = %s, HEARTRATEMAX = %s, HEARTRATEMIN = %s, ECG_DATA = %s WHERE ID = %s"
            # param = (add_time, heartRateAvg, heartRateMax, heartRateMin, data, ecgReport_id)
            try:
                cur.execute(sql, param)
                conn.commit()
            except:
                # 发生错误时回滚
                conn.rollback()
            ecg_data.clear()
            conn.close()

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
    global update_hr
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
                if start_save_ecg or update_hr:
                    ecg_data.append(json.loads(item['data'].decode()).get(PUBLISH_NAME))

    except:
        traceback.print_exc()
        is_quit = 1


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

    db_connection = connect(host='localhost', port=3306, database='health_monitor_sys', user='root', password='123456',
                           charset='utf8')
    cur = db_connection.cursor()

    # 收消息线程
    t0 = threading.Thread(target=receive)
    t0.setDaemon(True)
    t0.start()
    # 订阅消息线程
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
        time.sleep(0.1)

# 一个线程大概20m 4G内存 大概200人，使用gevent补丁可以增大2倍
