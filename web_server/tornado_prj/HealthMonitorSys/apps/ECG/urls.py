from tornado.web import url
from apps.ECG.handlers import EcgDataMonitor
from apps.ECG.handlers import DataMonitor
from apps.ECG.handlers import EcgDetection
from sockjs.tornado import SockJSRouter  # 定义路由的

# urlpattern = SockJSRouter(EcgDataMonitor.EcgRealTimeHandler, "/ecg/realtime").urls

urlpattern = (
    url("/start/realtime", DataMonitor.RealTimeHandler),
    url("/realtime_monitor/", EcgDataMonitor.MonitorHandler),
    url("/ecg/build_report/", EcgDetection.EcgBuildReportHandler),
    url("/ecg/data_table/", EcgDetection.EcgDataSaveHandler),
    # url("/ecg/report_list/", EcgDetection.EcgReportHandler),
    url("/ecg/get_report/([0-9]+)/detail/", EcgDetection.EcgReportDetailHandler),
    url("/ecg/report_list/", EcgDetection.EcgReportListHandler),
)
