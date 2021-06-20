from peewee import *
from HealthMonitor.models import BaseModel
from apps.users.models import User


class EcgTestReports(BaseModel):
    user = ForeignKeyField(User, verbose_name="用户id")
    ReportType = CharField(max_length=200, verbose_name="报告类别", null=True)
    heartRateAvg = SmallIntegerField(null=True, verbose_name="平均心率")
    heartRateMax = SmallIntegerField(null=True, verbose_name="最快心率")
    heartRateMin = SmallIntegerField(null=True, verbose_name="最慢心率")
    ecg_data = TextField(null=True, verbose_name="心电相关数据")
    hrv_parameter = TextField(null=True, verbose_name="HRV参数")
    diagnose = TextField(null=True, verbose_name="诊断结果")
    treament = TextField(null=True, verbose_name="治疗建议")
    tachycardia = SmallIntegerField(null=True, verbose_name="心动过速")
    bradycardia = SmallIntegerField(null=True, verbose_name="心动过缓")
    arrhythmia = SmallIntegerField(null=True, verbose_name="心率失常分类")
    arrhythmia_original = TextField(null=True, verbose_name="心率失常分类原始结果")
    # heartRate_data = TextField(null=True, verbose_name="心率数据")
    # start_time = TimeField(verbose_name='开始时间', null=True, default=None)
    # end_time = TimeField(verbose_name='结束时间', null=True, default=None)


class ECGData(BaseModel):
    ecgreport = ForeignKeyField(EcgTestReports, verbose_name="所属报告id")
    ecg_data = TextField(null=True, verbose_name="心电数据")
    create_date = DateField(verbose_name='创建日期', null=True, default=None)
    create_time = TimeField(verbose_name='创建时间', null=True, default=None)
