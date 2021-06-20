import json
from HealthMonitor.handler import RedisHandler
from apps.utils.hdm_decorators import authenticated_async
from apps.users.forms import ProfileForm, DeviceNoForm
from datetime import date
from apps.admin.models import Device



class ProfileHandler(RedisHandler):
    """获取个人信息"""

    @authenticated_async
    async def get(self, *args, **kwargs):
        user_birthday = self.current_user.birthday
        print(user_birthday)
        if user_birthday is None:
            init_birthday = "2000-01-01"
            user_birthday = date.fromisoformat(init_birthday)

        re_data = {
            "mobile": self._current_user.mobile,
            "nick_name": self.current_user.nick_name,
            "gender": self.current_user.gender,
            "address": self.current_user.address,
            "desc": self.current_user.desc,
            "birthday": user_birthday.strftime('%Y-%m-%d'),
            "age": self.current_user.age,
            "height": self.current_user.height,
            "weight": self.current_user.weight
        }
        self.finish(re_data)

    """修改个人信息"""

    @authenticated_async
    async def patch(self, *args, **kwargs):
        '''
        为什么使用patch:post一般用于新建,put更新整个字段，修改个人信息只能修改部分信息，登录账号不能修改
        patch专门用于部分字段更新
        '''
        re_data = {}
        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        profile_form = ProfileForm.from_json(param)
        if profile_form.validate():
            self.current_user.nick_name = profile_form.nick_name.data
            self.current_user.gender = profile_form.gender.data
            self.current_user.address = profile_form.address.data
            self.current_user.desc = profile_form.desc.data
            self.current_user.birthday = profile_form.birthday.data
            self.current_user.age = profile_form.age.data
            self.current_user.height = profile_form.height.data
            self.current_user.weight = profile_form.weight.data

            await self.application.objects.update(self.current_user)
        else:
            self.set_status(400)
            for field in profile_form.errors:
                re_data[field] = profile_form.errors[field][0]
        self.finish(re_data)


class HeadImageHandler(RedisHandler):
    @authenticated_async
    async def post(self, *args, **kwargs):
        re_data = {}
        pass


class InputDeviceNoHandler(RedisHandler):
    @authenticated_async
    async def get(self, *args, **kwargs):
        re_data = {
            "device_no": self.current_user.device_no,
        }
        self.finish(re_data)

    @authenticated_async
    async def patch(self, *args, **kwargs):
        '''
        用户注册登录系统后，需要提交产品序列号进行标识
        '''
        re_data = {}
        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        deviceno_form = DeviceNoForm.from_json(param)
        if deviceno_form.validate():
            # self.current_user.device_no = deviceno_form.device_no.data
            # await self.application.objects.update(self.current_user)
            device_no = deviceno_form.device_no.data
            try:
                device = await self.application.objects.get(Device, device_no=device_no)
                self.current_user.device_no = device.device_no
                await self.application.objects.update(self.current_user)
            except Device.DoesNotExist as e:
                self.set_status(401)
                re_data["device_non_existent"] = "所输入的设备序列号不存在"
        else:
            self.set_status(400)
            for field in deviceno_form.errors:
                re_data[field] = deviceno_form.errors[field][0]
        self.finish(re_data)
