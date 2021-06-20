# encoding:utf-8
import serial
import json
import binascii
from socket import *

# deviceno:2012290002
# device_no = [0xAA, 0xAA, 0x06, 0x14, 0x0C, 0x1D, 0x00, 0x02]
# device_no = json.dumps(device_no)
# device_no = bytes(device_no)
device_no = {'dev_no':'2012290002'}
device_no = json.dumps(device_no)

if __name__ == '__main__':
    print("start")
    send_data = False
    tcpClientSocket = socket(AF_INET, SOCK_STREAM)
    serAddr = ('*', 7788) # *处填入自己的远程ip
    tcpClientSocket.connect(serAddr)
    tcpClientSocket.send(device_no)

    # recvData = tcpClientSocket.recv(100)
    # print(type(recvData))
    # print(recvData)

    while send_data is False:
        recvData = tcpClientSocket.recv(100)
        print(type(recvData))
        print(recvData)
        if recvData == "send_data":
            send_data = True
        elif recvData == "send_device_no":
            tcpClientSocket.send(device_no)


    serial = serial.Serial('/dev/ttyS1', '115200')
    if serial.isOpen():
        print('Open sucess!!串口打开成功！\n')
    else:
        print('open failed串口打开失败！\n')
    try:
        getBytes = b''
        while True:
            count = serial.inWaiting()
            if count > 0:
                data = serial.read(count)
                if data != getBytes:
                    # print(binascii.b2a_hex(data))
                    # pass
                    tcpClientSocket.send(data)

    except KeyboardInterrupt:
        serial.close()
        tcpClientSocket.close()
