"""das URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.urls import resolve
import xadmin

from users.views import LoginView, LogoutView, ForgetPwdView, ModifyPwdView, ResetView
from users.views import RegisterView, UserActiveView
from users.views import CheckCodeValid

urlpatterns = [
    url(r'^check_code_valid/$', CheckCodeValid.as_view(), name='check_code_valid'),

    # TODO 以下功能为用户注册、激活、修改/找回密码功能。当前页面不限制需要登录，预留后期功能开发
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^useractive/(?P<active_code>.*)/$', UserActiveView.as_view(), name='useractive'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    url(r'^forget_pwd/$', ForgetPwdView.as_view(), name='forget_pwd'),
    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name='reset_pwd'),
    url(r'^modify_pwd/$', ModifyPwdView.as_view(), name='modify_pwd'),

]
