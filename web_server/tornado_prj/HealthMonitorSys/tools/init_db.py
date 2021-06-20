# from apps.users.models import *
from apps.admin.models import *
from apps.doctors.models import *
from apps.ECG.models import *
from peewee import MySQLDatabase

from HealthMonitor.settings import database

database = MySQLDatabase(
    'health_monitor_sys', host="127.0.0.1", port=3306, user="root", password="123456"
)


def init():
    # 生成表
    database.create_tables([User])
    database.create_tables([Admin, Device])
    database.create_tables([EcgTestReports])
    database.create_tables([Doctor])


if __name__ == "__main__":
    init()
