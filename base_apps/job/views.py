# -*- coding:utf-8 -*-
# @Time    : 2019-4-16 21:53
# @Author  : qingboy
# @Site    : 
# @File    : job_daily_summary.py
# @Software: PyCharm
import csv

import codecs
import pandas as pd
from django.http import HttpResponse
from django_pandas.io import read_frame
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from scipy import stats
from django.shortcuts import render
from django.views.generic.base import View
from .serializers import JobDetailSerializer
from .filters import JobDetailFilter

from .models import JobDetail
from .models import RecruitHistory

import json

from users.models import VerifyCodeRecord

from conf import GlobalConfig
global_config = GlobalConfig.GlobalConfig()
logger = global_config.logger_util("job_view", "job_view.log", logger_type="multi-process-rotating")
from utils.redis_util import init_cache_redis_conn
job_summary_cache = init_cache_redis_conn(1)
job_detail_cache = init_cache_redis_conn(2)
job_table_cache = init_cache_redis_conn(3)


def get_vistor_ip(request):
    return str(request.META.get('REMOTE_ADDR', '0.0.0.0')).split(' ')[0]


def index(request):
    return render(request, "index.html")


class IndexView(View):
    def get(self, request):
        return render(request, "index.html")


class JobSummary(View):
    def post(self, request):
        """
        接收页面搜索的关键字，返回对应关键字的历史统计数据
        先根据关键字从redis缓存获取，如有直接返回缓存数据
        如缓存无数据则根据汇总统计逻辑进行计算，并将计算结果存入redis缓存
        因基础数据仅在重新全量获取时才会更新，因此在获取全量数据时再清空所有缓存
        当访问量增大搜索关键字过多时，可在redis配置文件全局设置缓存过期时间
        :param request: 页面搜索的关键字
        :return: 招聘历史记录统计分析结果json数据
        """
        # 查找数据时用模糊匹配，统一小写方便从redis匹配key值
        key_word = request.POST.get("key_word", "").lower()
        summary_info = job_summary_cache.get(key_word)
        if summary_info:
            # 存在缓存数据，直接返回缓存数据
            logger.info("search key word:[%s] from [%s], response job_summary data from cache",
                        key_word, get_vistor_ip(request))
            return HttpResponse('{"status":"success","summary_info":"%s"}'
                                % summary_info, content_type="application/json")
        # 缓存数据不存在对应key值，从mysql读取数据并进行统计
        job_summary_df = read_frame(RecruitHistory.objects.filter(recruit_job_title__icontains=key_word).values \
                                        ("parse_date", "crawl_platform", "recruit_job_num", "recruit_company_num",
                                         "salary_min_avg", "salary_max_avg", "work_year_min_mode"))
        logger.info("search key word:[%s] from [%s], job_summary data set:%s",
                    key_word, get_vistor_ip(request), job_summary_df.shape)
        if job_summary_df.empty:
            return HttpResponse('{"status":"fail"}', content_type="application/json")
        else:
            # 统计汇总逻辑：按招聘平台、数据更新日期聚合
            # 求和：岗位数量、公司数量
            # 取均值：薪酬范围上/下限
            # 取众数：工作经验要求下限
            job_summary_tmp_df = (job_summary_df.groupby(["crawl_platform", "parse_date"]).agg(
                {
                    "recruit_job_num": ["sum"],
                    "recruit_company_num": ["sum"],
                    "salary_min_avg": ["mean"],
                    "salary_max_avg": ["mean"],
                    "work_year_min_mode": [lambda x: stats.mode(x)[0]]
                }))
            job_summary = pd.DataFrame(job_summary_tmp_df.values)
            job_summary = job_summary.rename(
                columns={0: "recruit_job_num", 1: "recruit_company_num", 2: "salary_min_avg",
                         3: "salary_max_avg", 4: "work_year_min_mode"})
            job_summary["crawl_platform"] = job_summary_tmp_df.index.levels[0].values[0]
            job_summary["parse_date"] = job_summary_tmp_df.index.levels[1]
            job_summary.reset_index(drop=True)
            summary_info = job_summary.round(decimals=0).T.to_json(orient="values", force_ascii=False)
            # 因基础数据仅在重新全量获取时才会更新，因此在获取全量数据时再清空所有缓存。此处无需设置过期时间
            job_summary_cache.set(key_word, str(summary_info).replace('"', "'"))
            logger.info("search key word:[%s] from [%s], job_summary group result:%s",
                        key_word, get_vistor_ip(request), summary_info)
            return HttpResponse('{"status":"success","summary_info":"%s"}' % (str(summary_info).replace('"', "'")),
                                content_type="application/json")


class JobDetailQuery(View):
    def get(self, request):
        """
        接收页面搜索的关键字，返回对应关键字的最新一次招聘的统计数据
        先根据关键字从redis缓存获取，如有直接返回缓存数据
        如缓存无数据则根据汇总统计逻辑进行计算，并将计算结果存入redis缓存
        因基础数据仅在重新全量获取时才会更新，因此在获取全量数据时再清空所有缓存
        当访问量增大搜索关键字过多时，可在redis配置文件全局设置缓存过期时间
        :param request: 页面搜索的关键字
        :return: 当前招聘记录统计分析结果json数据
        """
        # 查找数据时用模糊匹配，统一小写方便从redis匹配key值
        key_word = request.GET.get("key_word", "").lower()
        job_detail = job_detail_cache.get(key_word)
        if job_detail:
            # 存在缓存数据，直接返回缓存数据
            logger.info("search key word:[%s] from [%s], response job_detail data from cache",
                        key_word, get_vistor_ip(request))
            return HttpResponse('{"status":"success","job_detail":"%s"}'
                                % job_detail, content_type="application/json")
        # 缓存数据不存在对应key值，从mysql读取数据并进行统计
        job_detail_df = read_frame(
            JobDetail.objects.filter(Q(job_title__icontains=key_word) | Q(company_name__icontains=key_word)).values
            ("company_name", "job_title", "job_department", "job_address",
             "job_work_year_min", "job_degree", "job_major", "job_language",
             "job_hours_per_day", "job_days_per_week", "job_salary_min",
             "job_salary_max", "job_welfare", "job_summary", "job_url"))
        logger.info("search key word:[%s] from [%s], job_detail data set:%s",
                    key_word, get_vistor_ip(request), job_detail_df.shape)
        if job_detail_df.empty:
            return HttpResponse('{"status":"fail"}', content_type="application/json")
        else:
            # 分析招聘岗位薪酬范围分布，按薪酬范围进行拆箱分区统计，统计各薪酬区间的岗位数量
            salary_bin = [0, 1, 1000, 5000, 8000, 10000, 13000, 15000, 20000, 30000, 50000]
            salary_labels = ["面议", "<1k", "1k-5k", "5k-8k", "8k-10k", "10k-13k", "13k-15k", "15k-20k", "20k-30k", ">30k"]
            # 薪酬范围下限的岗位数量
            job_salary_min = []
            job_salary_min_count = pd.value_counts(
                pd.cut(job_detail_df["job_salary_min"], salary_bin, labels=salary_labels, include_lowest=True))
            # 匹配薪酬范围的标间及对应的统计值
            [job_salary_min.append(job_salary_min_count[salary_label]) for salary_label in salary_labels]
            # 薪酬范围上限的岗位数量
            job_salary_max = []
            job_salary_max_count = pd.value_counts(
                pd.cut(job_detail_df["job_salary_max"], salary_bin, labels=salary_labels, include_lowest=True))
            # 匹配薪酬范围的标间及对应的统计值
            [job_salary_max.append(job_salary_max_count[salary_label]) for salary_label in salary_labels]
            # 分析招聘岗位学历要求分布
            job_degree_tmp = job_detail_df["job_degree"].value_counts().to_dict()
            tmp = list()
            [tmp.append({"name": k, "value": job_degree_tmp[k]}) for (k, v) in job_degree_tmp.items()]
            job_degree = [tmp, list(job_degree_tmp.keys())]
            job_detail = [salary_labels, list(job_salary_min), list(job_salary_max), job_degree]
            # 因基础数据仅在重新全量获取时才会更新，因此在获取全量数据时再清空所有缓存。此处无需设置过期时间
            job_detail_cache.set(key_word, str(job_detail).replace('"', "'"))
            logger.info("search key word:[%s] from [%s], job_detail group result:%s",
                        key_word, get_vistor_ip(request), str(job_detail).replace('"', "'"))
            return HttpResponse('{"status":"success","job_detail":"%s"}' % (str(job_detail).replace('"', "'")),
                                content_type="application/json")


class JobDetailTable(View):
    def get(self, request):
        """
        接收页面搜索的关键字，返回对应关键字的最新一次招聘的明细数据
        先根据关键字从redis缓存获取，如有直接返回缓存数据
        如缓存无数据则从mysql取出数据后存入redis缓存
        因基础数据仅在重新全量获取时才会更新，因此在获取全量数据时再清空所有缓存
        当访问量增大搜索关键字过多时，可在redis配置文件全局设置缓存过期时间
        :param request: 页面搜索的关键字
        :return: 当前招聘记录明细数据
        """
        # 查找数据时用模糊匹配，统一小写方便从redis匹配key值
        key_word = request.GET.get("key_word", "").lower()
        job_table = job_table_cache.get(key_word)
        if job_table:
            # 存在缓存数据，直接返回缓存数据
            logger.info("search key word:[%s] from [%s], response job_table data from cache",
                        key_word, get_vistor_ip(request))
            return HttpResponse('{"status":"success","job_detail":"%s"}' % job_table, content_type="application/json")
        # 缓存数据不存在对应key值，从mysql读取数据并进行统计
        job_table_df = read_frame(
            JobDetail.objects.filter(Q(job_title__icontains=key_word) | Q(company_name__icontains=key_word)).values
            ("company_name", "job_title", "job_department", "job_address",
             "job_work_year_min", "job_degree", "job_major", "job_language",
             "job_hours_per_day", "job_days_per_week", "job_salary_min",
             "job_salary_max", "job_welfare", "job_summary", "job_url"))
        logger.info("search key word:[%s] from [%s], job_table data set:%s",
                    key_word, get_vistor_ip(request), job_table_df.shape)
        if job_table_df.empty:
            return HttpResponse('{"status":"fail"}', content_type="application/json")
        else:
            # df.to_json转换成json时空值显示为None，替换掉优化显示效果
            job_table_df.fillna(value="", inplace=True)
            job_table_df.replace([r'"', r"'"], "", inplace=True)
            # 薪酬范围上/下限空值替换为0
            job_table_df["job_salary_min"].replace([0, ""], "面议", inplace=True)
            job_table_df["job_salary_max"].replace([0, ""], "面议", inplace=True)
            job_table = (json.loads(job_table_df.to_json(orient='table', force_ascii=False)))["data"]
            # 因基础数据仅在重新全量获取时才会更新，因此在获取全量数据时再清空所有缓存。此处无需设置过期时间
            job_table_cache.set(key_word, str(job_table).replace('"', "'"))
            return HttpResponse('{"status":"success","job_detail":"%s"}' % (str(job_table).replace('"', "'")),
                                content_type="application/json")


class JobDownload(View):
    def get(self, request):
        """
        根据页面搜索的关键字及下载明细随机验证码，验证码通过后返回导出的excel文件
        下载验证码根据随机生成，生成模块详见users.views.CheckCodeValid
        :param request:搜索的关键字及下载明细随机验证码
        :return:导出的excel文件
        """
        download_auth_code = request.GET.get("download_auth_code", "")
        download_auth_record = VerifyCodeRecord.objects.filter(verify_code=download_auth_code, code_is_valid=True,
                                                               verify_type="download_auth_code")
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        key_word = request.GET.get("key_word", "")
        if download_auth_record:
            job_detail_df = read_frame(JobDetail.objects.filter(job_title__icontains=key_word).values
                                       ("company_name", "job_title", "job_department", "job_address",
                                        "job_work_year_min", "job_degree", "job_major", "job_language",
                                        "job_hours_per_day", "job_days_per_week", "job_salary_min",
                                        "job_salary_max", "job_welfare", "job_summary", "job_url"))
            logger.info("download key word:%s, download_auth_code:%s, job_table data set:%s",
                        key_word, download_auth_code, job_detail_df.shape)
            if job_detail_df.empty:
                response['Content-Disposition'] = 'attachment; filename="None_of_Search.xls"'
                writer.writerow(["查无招聘记录"])
                return response
            else:
                job_detail_df.fillna(value="", inplace=True)
                job_detail_table = (json.loads(job_detail_df.to_json(orient='table', force_ascii=False)))["data"]
                response['Content-Disposition'] = 'attachment; filename="Recruit_record.xls"'
                # 写入表头
                writer.writerow(
                    ["职位名称", "月薪低值", "月薪高值", "公司名称", "职位概述", "职位部门", "学历要求", "工作经验",
                     "专业要求", "工作地址", "天工作时长", "周工作天数", "福利待遇", "语言要求", "职位链接"])
                # 遍历写入每行数据
                [writer.writerow([data["job_title"], data["job_salary_min"], data["job_salary_max"],
                                  data["company_name"], data["job_summary"], data["job_department"], data["job_degree"],
                                  data["job_work_year_min"], data["job_major"], data["job_address"],
                                  data["job_hours_per_day"], data["job_days_per_week"], data["job_welfare"],
                                  data["job_language"], data["job_url"]]) for data in job_detail_table]
            # 将验证码置为无效，避免使用同一个验证码重复请求下载
            download_auth_record[0].code_is_valid = False
            download_auth_record[0].save()
            return response
        else:
            response['Content-Disposition'] = 'attachment; filename="Download_auth_fail.xls"'
            writer.writerow(["验证失败"])
            logger.info("download key word:%s, download_auth_code invalid:%s", key_word, download_auth_code)
            return response


# TODO restful-api 待前后端分离后使用
class JobDetailPagination(PageNumberPagination):
    # 设置分页参数
    page_size = 50
    page_size_query_param = 'page_size'
    page_query_param = 'p'
    max_page_size = 1000


class JobDetailViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = JobDetail.objects.all()
    pagination_class = JobDetailPagination
    serializer_class = JobDetailSerializer
    # 搜索rest_framework下的filters
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filter_class = JobDetailFilter
    search_fields = ("job_title", "company_name", "job_summary")

    # 排序
    # filter_backends = (filters.OrderingFilter,)
    ordering_fields = ("job_title", "company_name")
