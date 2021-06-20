import json
import jwt
import requests
from datetime import datetime
from datetime import date
from HealthMonitor.settings import settings

current_time = datetime.utcnow()

web_url = "http://127.0.0.1:8008"
data = jwt.encode({
    "id": 7,
    "nick_name": "taylen",
    "exp": current_time
}, settings["secret_key"]).decode("utf8")
headers = {
    "tsessionid": data
}


def test_sms():
    url = "{}/code/".format(web_url)
    data = {
        "mobile": "13570457628"
    }
    res = requests.post(url, json=data)

    print(json.loads(res.text))
    # print(res.text)


def test_register():
    url = "{}/register/".format(web_url)
    data = {
        "mobile": "13570457628",
        "code": "0755",
        "password": "admin123"
    }
    res = requests.post(url, json=data)

    print(json.loads(res.text))


def test_CheckLogin():
    data = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwibmlja19uYW1lIjoidGF5bGVuIiwiZXhwIjoxNjA4NjE3NzA3fQ.xJasj-_yxNoAWGNbs_etkOXBdDBFi8Vw1gx2JpB72fk"
    url = "{}/check_login/".format(web_url)
    requests.get(url, headers={
        "tsessionid": data
    })


def modify_profile():
    # 修改个人信息
    data = {
        "nick_name": "Taylen",
        "gender": "male",
        "desc": "抽烟、喝酒",
        "address": "四川省成都市高新区",
        "birthday": "1994-07-04",
        "age": 27,
        "height": 180,
        "weight": 70
    }
    url = "{}/user_info/".format(web_url)
    res = requests.patch(url, headers=headers, json=data)
    print(res.status_code)
    print(json.loads(res.text))


def get_profile():
    url = "{}/user_info/".format(web_url)
    res = requests.get(url, headers=headers)
    print(res.status_code)
    print(json.loads(res.text))


def modify_password():
    # 修改密码
    data = {
        "old_password": "123456",
        "new_password": "12345678",
        "confirm_password": "12345678",
    }
    url = "{}/password/".format(web_url)
    res = requests.post(url, headers=headers, json=data)
    print(res.status_code)
    print(json.loads(res.text))


if __name__ == "__main__":
    # test_sms()
    # test_register()
    # test_CheckLogin()
    # modify_profile()
    # get_profile()
    # modify_password()

    # data = set()
    # data.add("taylen")
    # data.add("taylen1")
    # data.clear()
    init_birthday = '2000-01-01'
    user_birthday = date.fromisoformat(init_birthday)
    print(user_birthday)


