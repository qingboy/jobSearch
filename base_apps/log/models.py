#-*- encoding:utf-8 -*-
from datetime import datetime


from django.db import models


from users.models import UserProfile
# Create your models here.


class UserLog(models.Model):
    operation_user = models.ForeignKey(UserProfile, verbose_name=u"操作用户名",on_delete=models.CASCADE)
    operation_time = models.DateTimeField(default=datetime.now,verbose_name=u"操作时间")
    operation_detail = models.CharField(max_length=200, default="", verbose_name=u"操作详情")
    operation_before = models.CharField(max_length=250, default="", verbose_name=u"操作前")
    operation_after = models.CharField(max_length=250, default="", verbose_name=u"操作后")

    class Meta:
        verbose_name = u"用户日志"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}{1}'.format(self.operation_time, self.operation_user)


class ServerLog(models.Model):
    request_user = models.ForeignKey(UserProfile, verbose_name=u"访问用户",on_delete=models.CASCADE)
    request_user_name = models.CharField(max_length=200, default="", verbose_name=u"访问用户名")
    request_time = models.DateTimeField(default=datetime.now, verbose_name=u"访问时间")
    request_ip = models.GenericIPAddressField(protocol="ipv4", verbose_name=u"访问IP")
    request_function = models.CharField(max_length=200, default="", blank=True, null=True, verbose_name=u"访问功能")
    request_param = models.TextField(default="", blank=True, null=True, verbose_name=u"请求参数")
    response_data = models.TextField(default="", blank=True, null=True, verbose_name=u"返回数据")

    class Meta:
        verbose_name = u"访问日志"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}{1}{2}'.format(self.request_time, self.request_user_name, self.request_function)


class CrawlLog(models.Model):
    crawl_time = models.DateTimeField(default=datetime.now, verbose_name=u"获取时间")
    crawl_status = models.BooleanField(default=False, verbose_name=u"获取状态")
    run_method = models.CharField(max_length=200, verbose_name=u"调用方法")
    run_parma = models.CharField(max_length=200, verbose_name=u"调用参数")

    class Meta:
        verbose_name = u"获取日志"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}{1}{2}'.format(self.crawl_time, self.run_method,self.crawl_status)


class ProxyIP(models.Model):
    update_time = models.DateTimeField(default=datetime.now, verbose_name=u"更新时间")
    ip = models.CharField(max_length=20, verbose_name=u"IP",primary_key=True)
    port = models.PositiveIntegerField(verbose_name=u"端口号")
    speed = models.FloatField(default=0.0, blank=True, null=True, verbose_name=u"连接速度")
    supplier = models.CharField(max_length=50, default="", verbose_name=u"提供方")
    address = models.CharField(max_length=100, default="", verbose_name=u"归属地")
    proxy_type = models.CharField(max_length=5, default="HTTP", verbose_name=u"代理类型")

    class Meta:
        verbose_name = u"代理IP池"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}{1}'.format(self.ip, self.port)

