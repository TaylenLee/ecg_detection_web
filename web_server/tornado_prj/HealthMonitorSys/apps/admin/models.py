from peewee import *
from bcrypt import hashpw, gensalt  # 用于加密
from HealthMonitor.models import BaseModel


class PasswordHash(bytes):
    def check_password(self, password):
        password = password.encode('utf-8')
        return hashpw(password, self) == self


class PasswordField(BlobField):
    def __init__(self, iterations=12, *args, **kwargs):
        if None in (hashpw, gensalt):
            raise ValueError('Missing library required for PasswordField: bcrypt')
        self.bcrypt_iterations = iterations
        self.raw_password = None
        super(PasswordField, self).__init__(*args, **kwargs)

    def db_value(self, value):
        """Convert the python value for storage in the database."""
        if isinstance(value, PasswordHash):
            return bytes(value)

        if isinstance(value, str):
            value = value.encode('utf-8')
        salt = gensalt(self.bcrypt_iterations)
        return value if value is None else hashpw(value, salt)

    def python_value(self, value):
        """Convert the database value to a pythonic value."""
        if isinstance(value, str):
            value = value.encode('utf-8')

        return PasswordHash(value)


class Admin(BaseModel):
    nick_name = CharField(max_length=20, null=True, verbose_name="昵称")
    mobile = CharField(max_length=11, verbose_name="手机号码", index=True, unique=True)
    password = PasswordField(verbose_name="密码")  # 1. 密文，2.不可反解


class Device(BaseModel):
    device_no = CharField(max_length=10, null=True, verbose_name="设备序列号", unique=True)
