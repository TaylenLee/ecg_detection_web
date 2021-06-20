import json
from HealthMonitor.handler import RedisHandler
from apps.utils.hdm_decorators import admin_authenticated_async
from apps.users.forms import ProfileForm, DeviceNoForm
from datetime import date
from apps.users.models import User
from apps.doctors.models import Doctor
from apps.ECG.models import EcgTestReports
from apps.admin.models import Admin, Device


class ProfileHandler(RedisHandler):
    """获取个人信息"""

    @admin_authenticated_async
    async def get(self, *args, **kwargs):
        re_data = {
            "mobile": self.current_user.mobile,
        }
        self.finish(re_data)


class UserListHandler(RedisHandler):
    """获取所有用户信息"""

    @admin_authenticated_async
    async def get(self, *args, **kwargs):
        re_data = []
        try:
            userList_query = User.select()
            userList = await self.application.objects.execute(userList_query)
            for user in userList:
                usertInfo = {}
                usertInfo = {
                    "nick_name": user.nick_name,
                    "mobile": user.mobile,
                    "age": user.age,
                    "address": user.address,
                    "add_time": user.add_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "device_no": user.device_no,
                    "user_id": user.id
                }
                re_data.append(usertInfo)
        except User.DoesNotExist as e:
            self.set_status(404)
        self.finish(json.dumps(re_data))

    """删除用户"""

    @admin_authenticated_async
    async def post(self, deleteUserId, *args, **kwargs):
        re_data = {}
        deleteUserId = await self.application.objects.get(User, id=int(deleteUserId))
        try:
            reportList_query = EcgTestReports.select().where(EcgTestReports.user == deleteUserId)
            reports = await self.application.objects.execute(reportList_query)
            for report in reports:
                await self.application.objects.delete(report)
        except EcgTestReports.DoesNotExist as e:
            self.set_status(404)
        await self.application.objects.delete(deleteUserId)
        self.finish(re_data)
        pass


class DoctorListHandler(RedisHandler):
    """获取所有医生用户信息"""

    @admin_authenticated_async
    async def get(self, *args, **kwargs):
        re_data = []
        try:
            doctorList_query = Doctor.select()
            doctorList = await self.application.objects.execute(doctorList_query)
            for doctor in doctorList:
                usertInfo = {}
                usertInfo = {
                    "nick_name": doctor.nick_name,
                    "mobile": doctor.mobile,
                    "age": doctor.age,
                    "address": doctor.address,
                    "add_time": doctor.add_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "doctor_id": doctor.id
                }
                re_data.append(usertInfo)
        except User.DoesNotExist as e:
            self.set_status(404)
        self.finish(json.dumps(re_data))

    """删除医生用户"""

    @admin_authenticated_async
    async def post(self, deleteDoctorId, *args, **kwargs):
        re_data = {}
        deleteDoctorId = await self.application.objects.get(Doctor, id=int(deleteDoctorId))
        # try:
        #     reportList_query = EcgTestReports.select().where(EcgTestReports.user == deleteUserId)
        #     reports = await self.application.objects.execute(reportList_query)
        #     for report in reports:
        #         await self.application.objects.delete(report)
        # except EcgTestReports.DoesNotExist as e:
        #     self.set_status(404)
        await self.application.objects.delete(deleteDoctorId)
        self.finish(re_data)


class AddDeviceNoHandler(RedisHandler):
    """获取所有设备序列号信息"""

    @admin_authenticated_async
    async def get(self, *args, **kwargs):
        re_data = []
        try:
            deviceList_query = Device.select()
            deviceList = await self.application.objects.execute(deviceList_query)
            for device in deviceList:
                deviceInfo = {}
                deviceInfo = {
                    "device_no": device.device_no
                }
                re_data.append(deviceInfo)
        except Device.DoesNotExist as e:
            self.set_status(404)
        self.finish(json.dumps(re_data))

    """添加新设备"""

    @admin_authenticated_async
    async def post(self, *args, **kwargs):
        re_data = {}
        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        deviceList = param['deviceList']
        for device in deviceList:
            # await self.application.object.create(Device,)
            device_no = device['device_no']
            try:
                existed_device = await self.application.objects.get(Device, device_no=device_no)
                self.set_status(400)
                re_data["device_existed"] = device_no
            except Device.DoesNotExist as e:
                device = await self.application.objects.create(Device, device_no=device_no)
        self.finish(re_data)
