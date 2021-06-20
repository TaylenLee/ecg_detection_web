from wtforms_tornado import Form
from wtforms import StringField, DateField, IntegerField
from wtforms.validators import DataRequired, Regexp, AnyOf  # Regexp为正则表达式

MOBILE_REGEX = "^1[358]\d{9}$|^1[48]7\d{8}$|^176\d{8}$"  # 手机正则表达式


class SmsCodeForm(Form):
    mobile = StringField("手机号码",
                         validators=[DataRequired(message="请输入手机号码"), Regexp(MOBILE_REGEX, message="请输入合法的手机号码")])


class LoginForm(Form):
    mobile = StringField("手机号码",
                         validators=[DataRequired(message="请输入手机号码"), Regexp(MOBILE_REGEX, message="请输入合法的手机号码")])
    password = StringField("密码", validators=[DataRequired(message="请输入密码")])


class RegisterForm(Form):
    mobile = StringField("手机号码",
                         validators=[DataRequired(message="请输入手机号码"), Regexp(MOBILE_REGEX, message="请输入合法的手机号码")])
    code = StringField("验证码", validators=[DataRequired(message="请输入验证码")])
    password = StringField("密码", validators=[DataRequired(message="请输入密码")])


class ProfileForm(Form):
    nick_name = StringField("昵称", validators=[DataRequired("请输入昵称")])
    gender = StringField("性别", validators=[AnyOf(values=["female", "male"])])
    address = StringField("地址", validators=[DataRequired("请输入地址")])
    age = IntegerField("年龄", validators=[DataRequired("请输入年龄")])


class ChangePasswordForm(Form):
    old_password = StringField("旧密码", validators=[DataRequired(message="请输入旧密码")])
    new_password = StringField("新密码", validators=[DataRequired(message="请输入新密码")])
    confirm_password = StringField("确认密码", validators=[DataRequired(message="请输入确认密码")])


class DiagnoseForm(Form):
    diagnose = StringField("诊断结果", validators=[DataRequired("请输入诊断结果")])
    treament = StringField("治疗建议", validators=[DataRequired("请输入治疗建议")])
