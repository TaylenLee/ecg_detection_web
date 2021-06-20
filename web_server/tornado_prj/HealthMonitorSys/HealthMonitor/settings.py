import os

import peewee_async

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
settings = {
    # "static_path": "E:/taylen_workspace/PythonWorkSpace/HealthMonitorSys/static",
    "static_path": os.path.join(BASE_DIR, "static"),
    "static_url_prefix": "/static/",
    # "template_path": "templates",
    "template_path": os.path.join(BASE_DIR, "templates"),
    "secret_key": "ZGGA#Mp4yL4w5CDu",  # 生成的随机密钥
    "jwt_expire": 7 * 24 * 3600,
    "MEDIA_ROOT": os.path.join(BASE_DIR, "media"),
    "SITE_URL": "http://127.0.0.1:8008",
    "db": {
        "host": "127.0.0.1",
        "user": "root",
        "password": "123456",
        "name": "message",
        "port": 3306
    },
    "redis": {
        "host": "127.0.0.1"
    }
}

database = peewee_async.MySQLDatabase(
    'health_monitor_sys', host="127.0.0.1", port=3306, user="root", password="123456"
)
