# -*- encoding:utf-8 -*-
# author:qingboy


from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from utils.mixin_util import LoginRequiredMixin
from jobSearch.settings import DOWNLOAD_AUTH_CODE

from datetime import datetime

from .models import UserProfile, VerifyCodeRecord
from utils.mail_util import send_register_email, random_str

from conf import GlobalConfig

global_config = GlobalConfig.GlobalConfig()
logger = global_config.logger_util("users_view", "users_view.log", logger_type="multi-process-rotating")


# Create your views here.


class CheckCodeValid(View):
    def get(self, request):
        """
        下载岗位明细前验证是否关注微信公众号功能，关注微信公众号将随机返回一个验证码
        请求下载时根据微信公众号提供的验证码生成随机字符串回传页面，页面重定向请求job.views.JobDownload进行数据下载
        :param request:
        :return:
        """
        weixin_fork_code = request.GET.get("weixin_fork_code", "")
        code = VerifyCodeRecord.objects.filter(verify_code=weixin_fork_code, code_is_valid=True,
                                               verify_type="weixin_fork_code")
        if code:
            download_auth_code = VerifyCodeRecord()
            # 将随机生成的下载验证码存入mysql数据库
            download_auth_code.code_is_valid = True
            download_auth_code.verify_type = "download_auth_code"
            download_auth_code.verify_code = random_str(8)
            download_auth_code.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            download_auth_code.save()
            logger.info("weixin_fork_code is valid:%s", weixin_fork_code)
            return HttpResponse('{"status":"success","download_auth_code":"%s"}' % download_auth_code.verify_code,
                                content_type="application/json")
        else:
            logger.info("weixin_fork_code is invalid:%s", weixin_fork_code)
            return HttpResponse('{"status":"fail","err_msg":"验证码无效"}', content_type="application/json")


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


def page_not_found(request):
    # 全局404处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):
    # 全局500处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response


# TODO 以下功能为用户注册、激活、修改/找回密码功能。当前页面不限制需要登录，预留后期功能开发
class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            # 自定义用户验证模块，用户根据用户名、用户邮箱、注册手机号登录均可
            user = UserProfile.objects.get(Q(username=username) | Q(email=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            logger.exception(e)
            return None


class UserActiveView(View):
    def get(self, request, active_code):
        all_records = VerifyCodeRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return HttpResponse({"status": "fail", "msg": "激活链接无效！"})
        return HttpResponse("useractive.html", {"status": "success", "msg": "激活成功！"})


class RegisterView(View):
    def post(self, request):
        email = request.POST.get("email", "")
        username = request.POST.get("username", "")
        nick_name = request.POST.get("nick_name", "")
        password = request.POST.get("password", "")
        mobile = request.POST.get("mobile", "")
        gender = request.POST.get("gender", "")
        weixin_fork_code = request.POST.get("code", "")
        user_profile = UserProfile()
        user_profile.username = username
        user_profile.email = email
        user_profile.mobile = mobile
        user_profile.gender = gender
        user_profile.nick_name = nick_name
        user_profile.is_active = False
        if weixin_fork_code == DOWNLOAD_AUTH_CODE:
            user_profile.download_auth = True
        else:
            user_profile.download_auth = False
        user_profile.password = make_password(password)
        send_register_email(email, "register", user_profile.nick_name, password)
        user_profile.save()
        return HttpResponse('{"status":"success","email":"%s", "password":"%s"}' % (email, password),
                            content_type="application/json")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


class LoginView(View):
    def post(self, request):
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponse('{"status":"success", "msg":"%s"}' % str(user), content_type="application/json")
            else:
                return HttpResponse('{"status":"fail", "msg":"%s未激活</br>请登录注册邮箱点击用户激活链接！"}' % user.email,
                                    content_type="application/json")
        else:
            return HttpResponse('{"status":"fail", "msg":"用户名或密码错误！"}', content_type="application/json")


class ForgetPwdView(View):
    def post(self, request):
        email = request.POST.get("email", "")
        try:
            user = UserProfile.objects.get(email=email)
            if user.is_active:
                send_register_email(email, "forget", user.cnName)
                return HttpResponse('{"status":"success", "msg":"%s"}' % email, content_type="application/json")
            else:
                return HttpResponse('{"status":"fail", "msg":"%s</br>该用户尚未激活，请先点击激活链接！"}' % email,
                                    content_type="application/json")
        except:
            return HttpResponse('{"status":"fail", "msg":"%s</br>该邮箱未注册！"}' % email, content_type="application/json")


class ResetView(View):
    def get(self, request, active_code):
        all_records = VerifyCodeRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                codestatus = record.codeStatus
                email = record.email
                user = UserProfile.objects.get(email=email)
                if codestatus:
                    return HttpResponse(
                        {"status": "success", "codestatus": codestatus, "email": email, "active_code": active_code,
                         "resettip": "请输入【%s】的新密码" % user.email})
                else:
                    return HttpResponse(
                        {"status": 'fail', "codestatus": codestatus, "email": email, "active_code": active_code,
                         "resettip": "密码重置链接已失效，请重新获取！"})
        else:
            return HttpResponse({"status": 'fail', "active_code": active_code, "resettip": "密码重置链接无效，请重新获取！"})


class ModifyPwdView(View):
    def post(self, request):
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        active_code = request.POST.get("active_code", "")
        user = UserProfile.objects.get(email=email)
        user.password = make_password(password)
        user.save()
        if request.POST.get("type", "") == 'unlogin':
            records = VerifyCodeRecord.objects.get(code=active_code)
            records.codeStatus = 0
            records.save()
        send_register_email(email, "modifypwd", user.cnName, password)
        return HttpResponse('{"status":"success", "msg":"%s，密码重置为：%s"}' % (user.email, password),
                            content_type="application/json")
