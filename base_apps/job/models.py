#-*- encoding:utf-8 -*-
from datetime import datetime


from django.db import models
from django.core.validators import URLValidator


# Create your models here.


class JobDetail(models.Model):
    job_id = models.CharField(max_length=10, primary_key=True,default="",verbose_name=u"职位ID")
    update_time = models.DateField(default=datetime.now, verbose_name=u"更新时间")
    crawl_platform = models.CharField(max_length=50, verbose_name=u"获取平台")
    refresh_date = models.DateField(default=datetime.now, blank=True, null=True, verbose_name=u"刷新日期")
    publish_date = models.DateField(default=datetime.now, blank=True, null=True, verbose_name=u"发布日期")
    is_valid_now = models.BooleanField(default=True, verbose_name=u"当前是否有效")
    company_name = models.CharField(max_length=100, default="", verbose_name=u"公司名称")
    job_title = models.CharField(max_length=50, default="", verbose_name=u"职位名称")
    job_department = models.CharField(max_length=50, default="", verbose_name=u"职位部门")
    job_rank = models.CharField(max_length=50, default="", verbose_name=u"职位级别")
    job_summary = models.TextField(default="", blank=True, null=True, verbose_name=u"职位概述")
    job_province = models.CharField(max_length=50, default="", blank=True, null=True, verbose_name=u"工作省份")
    job_city = models.CharField(max_length=50, default="", blank=True, null=True, verbose_name=u"工作城市")
    job_district = models.CharField(max_length=50, default="", blank=True, null=True, verbose_name=u"行政区")
    job_address = models.CharField(max_length=250, default="", blank=True, null=True, verbose_name=u"工作地址")
    job_work_year_min = models.PositiveIntegerField(default=0, blank=True, null=True,verbose_name=u"经验低值")
    job_work_year_max = models.PositiveIntegerField(default=0, blank=True, null=True,verbose_name=u"经验高值")
    job_degree = models.CharField(max_length=200, default="", blank=True, null=True, verbose_name=u"学历要求")
    job_language = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name=u"语言要求")
    job_major = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name=u"专业要求")
    job_age_min = models.PositiveIntegerField(default=18, verbose_name=u"年龄低值")
    job_age_max = models.PositiveIntegerField(blank=True, null=True, verbose_name=u"年龄高值")
    job_hours_per_day = models.PositiveIntegerField(default=8, verbose_name=u"天工作时长")
    job_days_per_week = models.PositiveIntegerField(default=5, verbose_name=u"周工作天数")
    job_salary_min = models.PositiveIntegerField(default=None, blank=True, null=True, verbose_name=u"月薪低值")
    job_salary_max = models.PositiveIntegerField(default=None, blank=True, null=True, verbose_name=u"月薪高值")
    job_welfare = models.TextField(default="", blank=True, null=True, verbose_name=u"福利待遇")
    job_type = models.CharField(max_length=20,default=u"全职", blank=True, null=True, verbose_name=u"职位性质")
    job_advantage = models.TextField(default="", blank=True, null=True, verbose_name=u"职位优势")
    job_require = models.TextField(default="", blank=True, null=True, verbose_name=u"职位要求")
    job_responsibilities = models.TextField(default="", blank=True, null=True, verbose_name=u"职位职责")
    job_url = models.TextField(validators=[URLValidator()], verbose_name=u"职位链接")
    job_email = models.CharField(max_length=50, default="", verbose_name=u"职位邮箱")
    job_response_ratio = models.FloatField(default=0.0, blank=True, null=True, verbose_name=u"回复率")

    class Meta:
        verbose_name = u"岗位详情"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}{1}'.format(self.company_name, self.job_title)


class CompanyInfo(models.Model):
    update_time = models.DateTimeField(default=datetime.now, verbose_name=u"更新时间")
    crawl_platform = models.CharField(max_length=50, verbose_name=u"获取平台")
    company_name = models.CharField(max_length=100, verbose_name=u"企业名称")
    company_type = models.CharField(max_length=50, default="", blank=True, null=True, verbose_name=u"企业性质")
    company_province = models.CharField(max_length=50, default="", blank=True, null=True, verbose_name=u"企业省份")
    company_city = models.CharField(max_length=50, default="", blank=True, null=True, verbose_name=u"企业城市")
    company_address = models.CharField(max_length=250, default="", blank=True, null=True, verbose_name=u"企业地址")
    company_employ_max = models.PositiveIntegerField(default=None, blank=True, null=True,verbose_name=u"员工数低值")
    company_employ_min = models.PositiveIntegerField(default=None, blank=True, null=True,verbose_name=u"员工数高值")
    company_stage = models.CharField(max_length=200, default="", blank=True, null=True, verbose_name=u"发展阶段")
    company_industry = models.CharField(max_length=200, default="", blank=True, null=True, verbose_name=u"所属行业")
    company_advantage = models.TextField(default="", blank=True, null=True, verbose_name=u"竞争优势")
    company_invest_institution = models.TextField(default="", blank=True, null=True, verbose_name=u"投资机构")
    company_website = models.CharField(max_length=250, default="", blank=True, null=True, verbose_name=u"企业官网")
    company_description = models.TextField(default="", blank=True, null=True, verbose_name=u"企业描述")

    class Meta:
        verbose_name = u"公司信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}{1}'.format(self.company_name, self.crawl_platform)


class RecruitHistory(models.Model):
    summary_id = models.CharField(max_length=100, default="", primary_key=True, verbose_name=u"汇总id")
    parse_date = models.CharField(max_length=20,default="", verbose_name=u"获取日期")
    update_time = models.DateTimeField(default=datetime.now, verbose_name=u"更新时间")
    crawl_platform = models.CharField(max_length=50, verbose_name=u"获取平台")
    recruit_job_title = models.CharField(max_length=50, verbose_name=u"职位名称")
    recruit_job_num = models.PositiveIntegerField(default=None, blank=True, null=True,verbose_name=u"招聘岗位数量")
    recruit_company_num = models.PositiveIntegerField(default=None, blank=True, null=True,verbose_name=u"招聘公司数量")
    salary_min_avg = models.PositiveIntegerField(default=None, blank=True, null=True, verbose_name=u"月薪低值均值")
    salary_max_avg = models.PositiveIntegerField(default=None, blank=True, null=True, verbose_name=u"月薪高值均值")
    work_year_min_mode = models.PositiveIntegerField(blank=True, null=True,verbose_name=u"经验低值众数")
    work_year_max_mode = models.PositiveIntegerField(blank=True, null=True,verbose_name=u"经验高值众数")
    hours_per_day_mode = models.PositiveIntegerField(blank=True, null=True,verbose_name=u"天工作时长众数")
    days_per_week_mode = models.PositiveIntegerField(blank=True, null=True,verbose_name=u"周工作天数众数")
    # degree_mode = models.CharField(max_length=20, default="", blank=True, null=True, verbose_name=u"学历要求众数")

    class Meta:
        verbose_name = u"招聘历史"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}{1}{2}'.format(self.recruit_job_title, self.crawl_platform,self.recruit_job_num)


class UrlPattern(models.Model):
    update_time = models.DateTimeField(default=datetime.now, verbose_name=u"更新时间")
    platform = models.CharField(max_length=250, default="", verbose_name=u"招聘平台")
    category = models.CharField(max_length=250, default="", verbose_name=u"链接类别")
    prefix = models.CharField(max_length=250, default="", verbose_name=u"前缀")
    parameter = models.CharField(max_length=250, default="", blank=True, null=True, verbose_name=u"参数")
    sample = models.CharField(max_length=250, default="", blank=True, null=True, verbose_name=u"样例")

    class Meta:
        verbose_name = u"链接模式"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}{1}'.format(self.platform, self.category)

