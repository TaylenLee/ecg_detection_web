import json
from HealthMonitor.handler import RedisHandler
from apps.utils.hdm_decorators import doctor_authenticated_async
from apps.doctors.forms import ProfileForm


class ProfileHandler(RedisHandler):
    """获取个人信息"""

    @doctor_authenticated_async
    async def get(self, *args, **kwargs):

        re_data = {
            "mobile": self.current_user.mobile,
            "doctor_id": self.current_user.id,
            "nick_name": self.current_user.nick_name,
            "gender": self.current_user.gender,
            "address": self.current_user.address,
            "age": self.current_user.age
        }
        self.finish(re_data)

    """完善个人信息"""

    @doctor_authenticated_async
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
            self.current_user.age = profile_form.age.data
            await self.application.objects.update(self.current_user)
        else:
            self.set_status(400)
            for field in profile_form.errors:
                re_data[field] = profile_form.errors[field][0]
        self.finish(re_data)
