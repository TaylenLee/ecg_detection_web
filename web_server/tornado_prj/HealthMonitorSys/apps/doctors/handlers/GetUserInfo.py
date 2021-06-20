import json
from HealthMonitor.handler import RedisHandler
from apps.utils.hdm_decorators import doctor_authenticated_async
from apps.users.models import User
from apps.ECG.models import EcgTestReports
from apps.doctors.forms import DiagnoseForm

class UserListHandler(RedisHandler):
    """获取所有用户信息"""

    @doctor_authenticated_async
    async def get(self, *args, **kwargs):
        re_data = []
        try:
            userList_query = User.select().where(User.doctor_id == self.current_user.id)
            userList = await self.application.objects.execute(userList_query)
            for user in userList:
                if user.gender == "male":
                    gender = "男"
                else:
                    gender = "女"
                usertInfo = {}
                usertInfo = {
                    "nick_name": user.nick_name,
                    "mobile": user.mobile,
                    "age": user.age,
                    "gender": gender,
                    "height": user.height,
                    "weight": user.weight,
                    "address": user.address,
                    "user_id": user.id
                }
                re_data.append(usertInfo)
        except User.DoesNotExist as e:
            self.set_status(404)
        self.finish(json.dumps(re_data))


class EcgReportListHandler(RedisHandler):
    @doctor_authenticated_async
    async def get(self, userId, *args, **kwargs):
        """获取当前用户所有的检测报告"""
        re_data = []
        userId = int(userId)
        reportType = self.get_argument("reportType", None)
        try:
            user = await self.application.objects.get(User, id=userId)
            reportList_query = EcgTestReports.select().where((
                EcgTestReports.user == userId) & (EcgTestReports.ReportType == reportType))
            reports = await self.application.objects.execute(reportList_query)
            for report in reports:
                reportInfo = {}
                reportInfo = {
                    "nick_name": user.nick_name,
                    "add_time": report.add_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "ecgReportId": report.id
                }
                re_data.append(reportInfo)
        except EcgTestReports.DoesNotExist as e:
            self.set_status(404)

        self.finish(json.dumps(re_data))


class EcgReportDetailHandler(RedisHandler):
    @doctor_authenticated_async
    async def get(self, ecgReportId, *args, **kwargs):
        """获取报告详情"""
        re_data = {}
        try:
            ecgReport = await self.application.objects.get(EcgTestReports, id=int(ecgReportId))
            # ecg_data = ecgReport.ecg_data
            userId = ecgReport.user_id
            user = await self.application.objects.get(User, id=userId)
            heartRateAvg = ecgReport.heartRateAvg
            if heartRateAvg is None:
                re_data = {
                    "nick_name": user.nick_name,
                    "gender": user.gender,
                    "age": user.age,
                    "height": user.height,
                    "weight": user.weight,
                    "device_no": user.device_no,
                    "desc": user.desc,

                    "ecgReportId": ecgReport.id,
                    "ecgReportType": ecgReport.ReportType,
                    "add_time": ecgReport.add_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "ecg_data": ecgReport.ecg_data,
                    "ecgReportIsValid": False
                }
            else:
                re_data = {
                    "nick_name": user.nick_name,
                    "gender": user.gender,
                    "age": user.age,
                    "height": user.height,
                    "weight": user.weight,
                    "device_no": user.device_no,
                    "desc": user.desc,

                    "ecgReportId": ecgReport.id,
                    "ecgReportType": ecgReport.ReportType,
                    "add_time": ecgReport.add_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "ecg_data": ecgReport.ecg_data,
                    "hrv_parameter": ecgReport.hrv_parameter,
                    "ecgReportIsValid": True,
                    "heartRateAvg": ecgReport.heartRateAvg,
                    "heartRateMax": ecgReport.heartRateMax,
                    "heartRateMin": ecgReport.heartRateMin,
                    "diagnose": ecgReport.diagnose,
                    "treament": ecgReport.treament,
                    "tachycardia": ecgReport.tachycardia,
                    "bradycardia": ecgReport.bradycardia,
                    "arrhythmia": ecgReport.arrhythmia,
                    "arrhythmia_original": ecgReport.arrhythmia_original
                }

        except EcgTestReports.DoesNotExist as e:
            self.set_status(404)
        self.finish(re_data)

    @doctor_authenticated_async
    async def patch(self, ecgReportId, *args, **kwargs):
        re_data = {}
        try:
            ecgReport = await self.application.objects.get(EcgTestReports, id=int(ecgReportId))
            param = self.request.body.decode("utf-8")
            param = json.loads(param)
            diagnose_form = DiagnoseForm.from_json(param)
            if diagnose_form.validate():
                ecgReport.diagnose = diagnose_form.diagnose.data
                ecgReport.treament = diagnose_form.treament.data
                await self.application.objects.update(ecgReport)
            else:
                self.set_status(400)
                for field in diagnose_form.errors:
                    re_data[field] = diagnose_form.errors[field][0]
        except EcgTestReports.DoesNotExist as e:
            self.set_status(404)

        self.finish(re_data)