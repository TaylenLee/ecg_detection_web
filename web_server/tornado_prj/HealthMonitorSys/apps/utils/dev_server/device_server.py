import threading
import json
import time
import redis
import traceback
from socket import *

# 创建socket
tcpClientSocket = socket(AF_INET, SOCK_STREAM)
# 连接服务器
serAddr = ('192.168.8.1', 2002)
tcpClientSocket.connect(serAddr)

redis_cli = None  # redis 客户端
device_no = ""  # 设备唯一id
count = 0


class WrtnodeGateway:
    def __init__(self):
        self.ReceiveHeader1 = 0
        self.ReceiveHeader2 = 1
        self.WaitingData = 2
        self.ReceiveData1 = 3
        self.ReceiveData2 = 4
        self.ReceiveCheckCode = 5
        self.PacketHeader1 = 0xaa
        self.PacketHeader2 = 0xaa
        self.receive_state = self.ReceiveHeader1
        self.Count = 0
        self.DataLength = 0
        self.ECGDataHighByte = 0
        self.ECGDataLowByte = 0
        self.ECGData = 0.0
        self.AllowSendData = 0

    def ReceiveFiniteStates(self, rx_data):
        if self.receive_state == self.ReceiveHeader1:
            if rx_data == self.PacketHeader1:
                self.receive_state = self.ReceiveHeader2
        elif self.receive_state == self.ReceiveHeader2:
            if rx_data == self.PacketHeader2:
                self.receive_state = self.WaitingData
            else:
                self.receive_state = self.ReceiveHeader1
        elif self.receive_state == self.WaitingData:
            if self.Count == 2:
                self.receive_state = self.ReceiveData1
            else:
                self.Count += 1
        elif self.receive_state == self.ReceiveData1:
            if self.DataLength == 1:
                self.ECGData = self.ECGDataHighByte * 256.0 + rx_data
                if self.ECGData > 32767:
                    self.ECGData -= 65536
                self.ECGData = round((self.ECGData * 18.3) / 128.0 / 1000.0, 3)
                # print(self.ECGData)
                self.receive_state = self.ReceiveCheckCode
                self.DataLength = 0
                self.AllowSendData = 1
            else:
                self.DataLength += 1
                self.ECGDataHighByte = rx_data
        elif self.receive_state == self.ReceiveData2:
            if self.DataLength == 1:
                self.ECGData = self.ECGDataHighByte * 256 + rx_data
                if self.ECGData > 32767:
                    self.ECGData -= 65536
                self.ECGData = round((self.ECGData * 18.3) / 128.0 / 1000, 3) # 单位mv
                self.receive_state = self.ReceiveCheckCode
                self.AllowSendData = 1
            else:
                self.DataLength += 1
                self.ECGDataHighByte = rx_data
        elif self.receive_state == self.ReceiveCheckCode:
            self.receive_state = self.ReceiveHeader1
            self.Count = 0
            self.DataLength = 0


def sendToDo(str_msg):
    """
            发送实时消息
    msg: str(json)
    """
    global redis_cli
    global device_no
    global count
    try:
        redis_cli.publish(device_no + "_" + "ecg", str_msg)
        # count = count + 1
        # print(count)
    except:
        traceback.print_exc()


def send_data(wg_global):
    # count = 0
    while 1:
        rs = tcpClientSocket.recv(36)
        for rd in rs:
            wg_global.ReceiveFiniteStates(rd)
            if wg_global.AllowSendData == 1:
                # res = {"device_no": device_no, "ecg": wg_global.ECGData}
                res = {"ecg": wg_global.ECGData}
                # print(wg_global.ECGData)
                res = json.dumps(res)
                # count = count+1
                # print(count)
                sendToDo(res)
                wg_global.AllowSendData = 0
                # time.sleep(0.01)

        time.sleep(0.01)
    tcpClientSocket.close()

def start_connect():
    wg = WrtnodeGateway()

    t1 = threading.Thread(target=send_data, args=(wg,))
    t1.setDaemon(True)
    t1.start()

# 程序入口
if __name__ == "__main__":
    print("device server start service....")
    redis_cli = redis.Redis()
    device_no = "2012290002"
    # start_connect()
    wg = WrtnodeGateway()
    #
    # t1 = threading.Thread(target=send_data, args=(wg,))
    # t1.setDaemon(True)
    # t1.start()
    send_data(wg)


