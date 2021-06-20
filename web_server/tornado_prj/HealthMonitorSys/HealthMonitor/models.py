from datetime import datetime

from HealthMonitor.settings import database
from peewee import *

class BaseModel(Model):
    add_time = DateTimeField(default=datetime.now, verbose_name="添加时间")
    class Meta:
        database = database