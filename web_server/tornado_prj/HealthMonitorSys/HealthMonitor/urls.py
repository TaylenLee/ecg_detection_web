from apps.users import urls as user_urls
from apps.admin import urls as admin_urls
from apps.ECG import urls as ecg_urls
from apps.doctors import urls as doctor_urls
# from apps.ECG.handlers import EcgDataMonitor
# from sockjs.tornado import SockJSRouter  # 定义路由的


urlpattern = []
urlpattern += user_urls.urlpattern
urlpattern += admin_urls.urlpattern
urlpattern += ecg_urls.urlpattern
urlpattern += doctor_urls.urlpattern
# urlpattern += SockJSRouter(EcgDataMonitor, "/ecg_realtime").urls
print(urlpattern)
