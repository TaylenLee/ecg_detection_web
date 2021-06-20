import MySQLdb
import json
import time

conn = MySQLdb.connect(host='localhost', port=3306, db='eesy', user='root', passwd='123456', charset='utf8')
cursor1 = conn.cursor()

list = []
for i in range(15000):
    n = 1.01
    list.append(n)
    n = n + float(0.01)
print(list)
# conn.close()
data = {
    "ecgdata": list
}
data = json.dumps(data)
add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
sql = "INSERT INTO ACCOUNT(NAME,MONEY,ECGDATA,ADD_TIME) VALUES (%s,%s,%s,%s)"
param = ("taylenLEE", 5000, data, add_time)
n = cursor1.execute(sql, param)
print(n)
conn.commit()
conn.close()
# sql = "SELECT * FROM ACCOUNT WHERE ID = %s" % (20)
# cursor1.execute(sql)


# results = cursor1.fetchall()
# ecgdata = results[0][3]
# ecgdata = json.loads(ecgdata)
# print(type(ecgdata.get("ecgdata")))

print(add_time)
