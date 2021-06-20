from socket import *
import json
# 创建socket
tcpSerSocket = socket(AF_INET, SOCK_STREAM)

# 重复使用绑定的信息
tcpSerSocket .setsockopt(SOL_SOCKET, SO_REUSEADDR  , 1)

serAddr = ('', 7788)
tcpSerSocket.bind(serAddr)
tcpSerSocket.listen(5)
print("bind sucess!")
count = 0
newSocket, clientAddr = tcpSerSocket.accept()

while 1:
    device_no = None

    # rs = newSocket.recv(124)
    # str_dev_no = rs.decode()
    # dic_dev_no = json.loads(str_dev_no)
    # device_no = dic_dev_no.get('dev_no')
    # print(device_no)
    # print(type(device_no))
    # while device_no is None:
    #     newSocket.send("send_device_no")
    # newSocket.send("send_data")
    # count = count + 1
    #print(count)
    while device_no is None:
        rs = newSocket.recv(124)
        str_dev_no = rs.decode()
        dic_dev_no = json.loads(str_dev_no)
        device_no = dic_dev_no.get('dev_no')
        if device_no is None:
            newSocket.send("send_device_no".encode("utf8"))
        else:
            newSocket.send("send_data".encode("utf8"))
    print("over")
