from tornado.web import url
from apps.users.handlers import VerifyCode, Passport, Profile, DoctorProfile
# from apps.ECG.handlers import EcgDataMonitor
# from apps.ECG.handlers import DataMonitor

urlpattern = (
    url("/code/", VerifyCode.SmsHandler),
    url("/register/", Passport.RegisterHandler),
    url("/login/", Passport.LoginHandler),
    url("/check_login/", Passport.CheckLoginHandler),
    url("/user_info/", Profile.ProfileHandler),
    url("/headimages/", Profile.HeadImageHandler),
    url("/password/", Passport.ChangePasswordHandler),
    url("/input_deviceno/", Profile.InputDeviceNoHandler),
    url("/doctor_info/", DoctorProfile.ProfileHandler),
    url("/input_doctor_id/", DoctorProfile.InputDoctorIdHandler),
    # url("/realtime_monitor/", EcgDataMonitor.MonitorHandler),
    # url("/start/realtime", DataMonitor.RealTimeHandler),
)
