from tornado.web import url
from apps.admin.handlers import VerifyCode, Passport, Profile

urlpattern = (
    url("/code/", VerifyCode.SmsHandler),
    url("/admin/register/", Passport.RegisterHandler),
    url("/admin/login/", Passport.LoginHandler),
    url("/admin/user_info/", Profile.ProfileHandler),
    url("/admin/password/", Passport.ChangePasswordHandler),
    url("/admin/user_list/", Profile.UserListHandler),
    url("/admin/doctor_list/", Profile.DoctorListHandler),
    url("/admin/deleteUser/([0-9]+)/", Profile.UserListHandler),
    url("/admin/deleteDoctor/([0-9]+)/", Profile.DoctorListHandler),
    url("/admin/save_device/", Profile.AddDeviceNoHandler),
    url("/admin/device_list/", Profile.AddDeviceNoHandler),
)
