import json

from HealthMonitor.handler import RedisHandler
from apps.doctors.models import Doctor
from apps.users.forms import DoctorIdForm
from apps.utils.hdm_decorators import authenticated_async


class ProfileHandler(RedisHandler):
    """获取医生信息"""

    @authenticated_async
    async def get(self, *args, **kwargs):
        re_data = {}
        doctor_id = self.current_user.doctor_id
        if doctor_id is not None:
            doctor = await self.application.objects.get(Doctor, id=doctor_id)
            if doctor.gender == "male":
                gender = "男"
            else:
                gender = "女"
            re_data = {
                "mobile": doctor.mobile,
                "nick_name": doctor.nick_name,
                "gender": gender,
                "address": doctor.address,
                "age": doctor.age,
            }
        self.finish(re_data)


class InputDoctorIdHandler(RedisHandler):
    @authenticated_async
    async def get(self, *args, **kwargs):
        re_data = {
            "doctor_id": self.current_user.doctor_id,
        }
        self.finish(re_data)

    @authenticated_async
    async def patch(self, *args, **kwargs):
        '''
        用户可添加医生ID以便医生远程查看检测报告
        '''
        re_data = {}
        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        doctorId_form = DoctorIdForm.from_json(param)
        if doctorId_form.validate():
            doctor_id = doctorId_form.doctor_id.data
            try:
                doctor = await self.application.objects.get(Doctor, id=doctor_id)
                self.current_user.doctor_id = doctor.id
                await self.application.objects.update(self.current_user)
            except Doctor.DoesNotExist as e:
                self.set_status(401)
                re_data["doctor"] = "所输医生ID不存在"
        else:
            self.set_status(400)
            for field in doctorId_form.errors:
                re_data[field] = doctorId_form.errors[field][0]
        self.finish(re_data)
