import json
from peewee import *
from HealthMonitor.handler import RedisHandler
from apps.utils.hdm_decorators import authenticated_async
from apps.ECG.forms import BuildResportForm
from apps.ECG.models import EcgTestReports, ECGData
from HealthMonitor.settings import settings
from datetime import date
import redis
import time
from sockjs.tornado import SockJSConnection

import threading
import multiprocessing


class EcgBuildReportHandler(RedisHandler):
    """获取设备序列号与报告id"""

    @authenticated_async
    async def get(self, *args, **kwargs):
        re_data = {}
        ecgReportTime_query = EcgTestReports.select(fn.MAX(EcgTestReports.add_time)).where(
            EcgTestReports.user == self.current_user.id)
        query = EcgTestReports.select().where(EcgTestReports.add_time == ecgReportTime_query)
        current_EcgReport = await self.application.objects.execute(query)
        if current_EcgReport != None:
            ecgReport_id = current_EcgReport[0].id
            ecgReport_type = current_EcgReport[0].ReportType
        else:
            ecgReport_id = ""
        # for et in current_ecgReport:
        #     print(et.add_time)
        re_data = {
            # "user_id": self.current_user.id,
            "device_no": self.current_user.device_no,
            "ecgReport_id": ecgReport_id,
            "ecgReport_type": ecgReport_type
        }
        # print(self.current_user.device_no)
        self.finish(re_data)

    @authenticated_async
    async def post(self, *args, **kwargs):
        '''
        新建测试报告
        '''
        re_data = {}
        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        ecg_report_form = BuildResportForm.from_json(param)
        if ecg_report_form.validate():
            # user = ecg_report_form.user.data
            ReportType = ecg_report_form.ReportType.data
            ecgreport = await self.application.objects.create(EcgTestReports, user=self.current_user,
                                                              ReportType=ReportType)
            # ecgdata = await self.application.objects.create(ECGData, ecgreport=ecgreport)
            re_data["ecg_reportid"] = ecgreport.id
            # re_data["ecgdata_tableid"] = ecgdata.id
        else:
            self.set_status(400)
            for field in ecg_report_form.errors:
                re_data[field] = ecg_report_form.errors[field][0]
        self.finish(re_data)


class EcgDataSaveHandler(RedisHandler):
    @authenticated_async
    async def post(self, *args, **kwargs):
        '''
        新建ecgdata数据表
        '''
        ecgreport = self.get_argument("ecgreport", None)
        if ecgreport:
            print(ecgreport)
        # re_data = {}
        # param = self.request.body.decode("utf-8")
        # param = json.loads(param)
        # ecg_report_form = BuildResportForm.from_json(param)
        # if ecg_report_form.validate():
        #     # user = ecg_report_form.user.data
        #     ReportType = ecg_report_form.ReportType.data
        #     ecgreport = await self.application.objects.create(EcgTestReports, user=self.current_user,
        #                                                       ReportType=ReportType)
        #     re_data["ecg_reportid"] = ecgreport.id
        # else:
        #     self.set_status(400)
        #     for field in ecg_report_form.errors:
        #         re_data[field] = ecg_report_form.errors[field][0]
        # self.finish(re_data)


class EcgReportDetailHandler(RedisHandler):
    @authenticated_async
    async def get(self, ecgReportId, *args, **kwargs):
        """获取报告详情"""
        re_data = {}
        try:
            ecgReport = await self.application.objects.get(EcgTestReports, id=int(ecgReportId))
            # ecg_data = ecgReport.ecg_data
            heartRateAvg = ecgReport.heartRateAvg
            if heartRateAvg is None:
                re_data = {
                    "nick_name": self.current_user.nick_name,
                    "gender": self.current_user.gender,
                    "age": self.current_user.age,
                    "height": self.current_user.height,
                    "weight": self.current_user.weight,
                    "device_no": self.current_user.device_no,
                    "desc": self.current_user.desc,

                    "ecgReportId": ecgReport.id,
                    "ecgReportType": ecgReport.ReportType,
                    "add_time": ecgReport.add_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "ecg_data": ecgReport.ecg_data,
                    "ecgReportIsValid": False
                }
            else:
                re_data = {
                    "nick_name": self.current_user.nick_name,
                    "gender": self.current_user.gender,
                    "age": self.current_user.age,
                    "height": self.current_user.height,
                    "weight": self.current_user.weight,
                    "device_no": self.current_user.device_no,
                    "desc": self.current_user.desc,

                    "ecgReportId": ecgReport.id,
                    "ecgReportType": ecgReport.ReportType,
                    "add_time": ecgReport.add_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "ecg_data": ecgReport.ecg_data,
                    "hrv_parameter": ecgReport.hrv_parameter,
                    "ecgReportIsValid": True,
                    "heartRateAvg": ecgReport.heartRateAvg,
                    "heartRateMax": ecgReport.heartRateMax,
                    "heartRateMin": ecgReport.heartRateMin,
                    # "heartRate_data": ecgReport.heartRate_data,
                }

        except EcgTestReports.DoesNotExist as e:
            self.set_status(404)
        self.finish(re_data)
        pass


class EcgReportListHandler(RedisHandler):
    @authenticated_async
    async def get(self, *args, **kwargs):
        """获取当前用户所有的检测报告"""
        re_data = []
        reportType = self.get_argument("reportType", None)
        try:
            reportList_query = EcgTestReports.select().where((
                EcgTestReports.user == self.current_user.id) & (EcgTestReports.ReportType == reportType))
            reports = await self.application.objects.execute(reportList_query)
            for report in reports:
                reportInfo = {}
                reportInfo = {
                    "nick_name": self.current_user.nick_name,
                    "add_time": report.add_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "ecgReportId": report.id
                }
                re_data.append(reportInfo)
        except EcgTestReports.DoesNotExist as e:
            self.set_status(404)

        self.finish(json.dumps(re_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        '''
        新建ecgdata数据表
        '''
        ecgreport = self.get_argument("ecgreport", None)
        if ecgreport:
            print(ecgreport)
        # re_data = {}
        # param = self.request.body.decode("utf-8")
        # param = json.loads(param)
        # ecg_report_form = BuildResportForm.from_json(param)
        # if ecg_report_form.validate():
        #     # user = ecg_report_form.user.data
        #     ReportType = ecg_report_form.ReportType.data
        #     ecgreport = await self.application.objects.create(EcgTestReports, user=self.current_user,
        #                                                       ReportType=ReportType)
        #     re_data["ecg_reportid"] = ecgreport.id
        # else:
        #     self.set_status(400)
        #     for field in ecg_report_form.errors:
        #         re_data[field] = ecg_report_form.errors[field][0]
        # self.finish(re_data)
