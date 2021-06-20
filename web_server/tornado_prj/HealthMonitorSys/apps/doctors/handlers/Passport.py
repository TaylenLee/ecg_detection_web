import jwt
import json
from datetime import datetime
from HealthMonitor.handler import RedisHandler
from apps.doctors.forms import RegisterForm, LoginForm, ChangePasswordForm
from apps.doctors.models import Doctor
from apps.utils.hdm_decorators import doctor_authenticated_async


class LoginHandler(RedisHandler):
    async def post(self, *args, **kwargs):
        re_data = {}

        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        form = LoginForm.from_json(param)

        if form.validate():
            mobile = form.mobile.data
            password = form.password.data

            try:
                user = await self.application.objects.get(Doctor, mobile=mobile)
                # 将明文进行加密，和密文进行对比，并且加密过程不可逆
                if not user.password.check_password(password):
                    self.set_status(400)
                    re_data["non_fields"] = "用户名或密码错误"
                else:
                    # 登录成功
                    # 1. 是不是rest api只能使用jwt
                    # session实际上是服务器随机生成的一段字符串， 保存在服务器的
                    # jwt 本质上还是加密技术，不需要在服务器中保存，节省空间，例如可以直接解密出userid， user.name等（通过jwt生成token，返回给前端）

                    # 生成json web token; github上搜 Python jwt
                    payload = {
                        "id": user.id,
                        "nick_name": user.nick_name,
                        "exp": datetime.utcnow()  # 过期时间
                    }
                    token = jwt.encode(payload, self.settings["secret_key"], algorithm='HS256')
                    re_data["id"] = user.id
                    re_data["tel"] = user.mobile
                    if user.nick_name is not None:
                        re_data["nick_name"] = user.nick_name
                    else:
                        re_data["nick_name"] = user.mobile
                    re_data["token"] = token.decode("utf8")

            except Doctor.DoesNotExist as e:
                self.set_status(400)
                re_data["mobile"] = "用户不存在"

            self.finish(re_data)


class RegisterHandler(RedisHandler):
    async def post(self, *args, **kwargs):
        re_data = {}

        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        register_form = RegisterForm.from_json(param)
        if register_form.validate():
            mobile = register_form.mobile.data
            code = register_form.code.data
            password = register_form.password.data

            # 验证码是否正确
            redis_key = "{}_{}".format(mobile, code)
            if not self.redis_conn.get(redis_key):
                self.set_status(400)
                re_data["code"] = "验证码错误或者失效"
            else:
                # 验证用户是否存在
                try:
                    existed_users = await self.application.objects.get(Doctor, mobile=mobile)
                    self.set_status(400)
                    re_data["mobile"] = "用户已经存在"
                except Doctor.DoesNotExist as e:
                    user = await self.application.objects.create(Doctor, mobile=mobile, password=password)
                    re_data["id"] = user.id
        else:
            self.set_status(400)
            for field in register_form.errors:
                re_data[field] = register_form.errors[field][0]

        self.finish(re_data)



class ChangePasswordHandler(RedisHandler):
    @doctor_authenticated_async
    async def post(self, *args, **kwargs):
        # 修改密码
        re_data = {}
        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        password_form = ChangePasswordForm.from_json(param)
        if password_form.validate():
            # 检查旧密码
            if not self.current_user.password.check_password(password_form.old_password.data):
                self.set_status(400)
                re_data["old_password"] = "旧密码错误"
            else:
                if password_form.new_password.data != password_form.confirm_password.data:
                    self.set_status(400)
                    re_data["old_password"] = "两次密码不一致"
                else:
                    self.current_user.password = password_form.new_password.data
                    await self.application.objects.update(self.current_user)
        else:
            self.set_status(400)
            for field in password_form.errors:
                re_data[field] = password_form.errors[field][0]

        self.finish(re_data)