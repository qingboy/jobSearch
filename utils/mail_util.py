#-*- encoding:utf-8 -*-
# author:qingboy

from random import Random
from django.core.mail import send_mail

from users.models import VerifyCodeRecord
from jobSearch.settings import EMAIL_FROM


import datetime


def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str+=chars[random.randint(0, length)]
    return str


# TODO 以下功能为用户注册、激活、修改/找回密码功能。当前页面不限制需要登录，预留后期功能开发
def send_register_email(email, send_type,*userinfo):
    email_record = VerifyCodeRecord()
    if send_type == "update_email":
        verify_code = random_str(6)
    else:
        verify_code = random_str(16)

    if send_type == "register":
        email_record.verify_code = verify_code
        email_record.email = email
        email_record.sendType = send_type
        email_record.save()
        email_title = "全职搜注册激活链接"
        email_body = "hi~%s:   您在%s，注册了全职搜。信息如下：【用户名：%s，密码：%s】，请点击下面的链接激活你的账号: http://qingoy.com/users/useractive/%s"%(userinfo[0],datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),email,userinfo[1],verify_code)

        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass

    elif send_type == "forget":
        email_record.verify_code = verify_code
        email_record.email = email
        email_record.sendType = send_type
        email_record.save()
        email_title = "全职搜密码重置链接"
        email_body = "hi~%s:   您在%s申请重置%s的登录密码，请点击下面的链接重置密码: http://qingoy.com/users/reset/%s"%(userinfo[0],datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),email,verify_code)

        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass


    elif send_type == "modifypwd":
        email_title = "全职搜密码重置提醒"
        email_body = "hi~%s:   您在%s，重置了登录密码。信息如下：【用户名：%s，密码：%s】"%(userinfo[0],datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),email,userinfo[1])

        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
