# 云片短信平台
import requests


class YunPian:
    def __init__(self, api_key):
        self.api_key = api_key

    def send_single_sms(self,code, mobile):
        #发送单条短信
        url = "https://sms.yunpian.com/v2/sms/single_send.json"
        text = "您的验证码是{}。如非本人操作，请忽略本短信".format(code)
        res = requests.post(url, data={
            "apikey":self.api_key,
            "mobile":mobile,
            "text":text
        })

        return res

if __name__ == "__main__":
    yun_pian = YunPian("5af53b33680961******************")
    res = yun_pian.send_single_sms("1234", "13577887788")
    print(res.text)
