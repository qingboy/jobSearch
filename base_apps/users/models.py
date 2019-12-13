# -*- encoding:utf-8 -*-


from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class UserProfile(AbstractUser):
    nick_name = models.CharField(max_length=200, verbose_name=u"昵称")
    mobile = models.CharField(max_length=11, default="", blank=True, null=True, verbose_name=u"手机")
    gender = models.CharField(max_length=7, choices=(("male", u"男"), ("female", u"女")), default="female",
                              verbose_name=u"性别")
    download_auth = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name=u"下载权限")

    class Meta:
        verbose_name = u"用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class VerifyCodeRecord(models.Model):
    code_is_valid = models.BooleanField(default=False, verbose_name=u"验证码是否有效")
    mobile = models.CharField(max_length=11, default="", blank=True, null=True, verbose_name=u"手机")
    email = models.EmailField(blank=True, null=True, max_length=50, verbose_name=u"邮箱")
    create_time = models.DateTimeField(default=datetime.now, blank=True, null=True, verbose_name=u"创建时间")
    verify_type = models.CharField(max_length=50, verbose_name=u"验证码类型")
    verify_code = models.CharField(max_length=20, verbose_name=u"验证码")

    class Meta:
        verbose_name = u"验证码信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}{1}'.format(self.email, self.verify_code)
