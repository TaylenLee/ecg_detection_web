from socket import *
from threading import Thread
import json
import redis
import traceback
from time import sleep


class DataParsing:
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
        self.TemData = 0.0
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
                self.ECGData = round((self.ECGData * 18.3) / 128.0 / 1000, 3)  # 单位mv
                self.receive_state = self.ReceiveCheckCode
                self.AllowSendData = 1
            else:
                self.DataLength += 1
                self.ECGDataHighByte = rx_data
        elif self.receive_state == self.ReceiveCheckCode:
            self.receive_state = self.ReceiveHeader1
            self.Count = 0
            self.DataLength = 0


# 处理客户端的请求并执行事情
def dealWithClient(newSocket, destAddr, coon):
    # redis_cli = redis.StrictRedis(host='localhost', port=6379, db=0)
    device_no = None
    # 首先获取设备客户端发来的设备序列号
    while device_no is None:
        rs = newSocket.recv(100)
        str_dev_no = rs.decode()
        dic_dev_no = json.loads(str_dev_no)
        device_no = dic_dev_no.get('dev_no')
        if device_no is None:
            newSocket.send("send_device_no".encode("utf8"))
        else:
            newSocket.send("send_data".encode("utf8"))

    dataParsing = DataParsing()
    count = 0
    while True:
        recvData = newSocket.recv(1024)
        if len(recvData) > 0:
            # print('recv[%s]:%s' % (str(destAddr), recvData))
            for rd in recvData:
                dataParsing.ReceiveFiniteStates(rd)
                count = count + 1
                print(count)
                if dataParsing.AllowSendData == 1:
                    res = {"ecg": dataParsing.ECGData}
                    # print(dataParsing.ECGData)
                    res = json.dumps(res)
                    try:
                        coon.publish(device_no + "_" + "ecg", res)
                    except:
                        traceback.print_exc()
                    dataParsing.AllowSendData = 0
                    # sleep(0.01)
        else:
            print('[%s]客户端已经关闭' % str(destAddr))
            break
        sleep(0.01)

    newSocket.close()


def main():
    # 创建套接字
    serSocket = socket(AF_INET, SOCK_STREAM)
    # 设置可以重复使用绑定的信息
    serSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    # 绑定本机信息
    localAddr = ('', 2001)
    serSocket.bind(localAddr)
    # 变为被动
    serSocket.listen(100)

    # 拿到一个redis的连接池
    pool = redis.ConnectionPool(host='localhost', port=6379, max_connections=20)

    try:
        while True:
            print('-----主进程,等待新客户端的到来------')
            newSocket, destAddr = serSocket.accept()
            conn = redis.Redis(connection_pool=pool, decode_responses=True)
            print('-----主进程,接下来创建一个新的线程负责数据处理[%s]-----' % str(destAddr))
            client = Thread(target=dealWithClient, args=(newSocket, destAddr, conn))
            client.start()

            # 因为线程中共享这个套接字，如果关闭了会导致这个套接字不可用，
            # 但是此时在线程中这个套接字可能还在收数据，因此不能关闭
            # newSocket.close()
    finally:
        serSocket.close()


if __name__ == '__main__':
    main()
