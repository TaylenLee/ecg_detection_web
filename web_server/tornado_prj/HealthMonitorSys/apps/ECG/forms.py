from wtforms_tornado import Form
from wtforms import StringField, DateField, IntegerField
from wtforms.validators import DataRequired, Regexp, AnyOf  # Regexp为正则表达式


class BuildResportForm(Form):
    user = IntegerField("用户", validators=[DataRequired(message="用户id")])
    ReportType = StringField("报告类别", validators=[DataRequired(message="报告类别输入")])
