from tornado.web import url
from apps.doctors.handlers import VerifyCode, Passport, Profile, GetUserInfo

urlpattern = (
    url("/code/", VerifyCode.SmsHandler),
    url("/doctor/register/", Passport.RegisterHandler),
    url("/doctor/login/", Passport.LoginHandler),
    url("/doctor/password/", Passport.ChangePasswordHandler),
    url("/doctor/doctor_info/", Profile.ProfileHandler),
    url("/doctor/user_list/", GetUserInfo.UserListHandler),
    url("/doctor/report_list/([0-9]+)/", GetUserInfo.EcgReportListHandler),
    url("/doctor/get_report/([0-9]+)/detail/", GetUserInfo.EcgReportDetailHandler),
    # url("/admin/save_device/", Profile.AddDeviceNoHandler),
    # url("/admin/device_list/", Profile.AddDeviceNoHandler),
)
