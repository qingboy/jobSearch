# -*- encoding:utf-8 -*-
# author:qingboy

import xadmin
from xadmin import views

from .models import JobDetail, RecruitHistory, CompanyInfo, UrlPattern


class JobDetailAdmin(object):
    list_display = ["job_id", "update_time", "crawl_platform", "refresh_date", "publish_date", "is_valid_now",
                    "company_name", "job_title", "job_department", "job_rank", "job_summary", "job_province",
                    "job_city", "job_district", "job_address", "job_work_year_min", "job_work_year_max",
                    "job_degree", "job_major", "job_language", "job_age_min", "job_age_max", "job_hours_per_day",
                    "job_days_per_week", "job_salary_min", "job_salary_max", "job_welfare", "job_type",
                    "job_advantage", "job_require", "job_responsibilities", "job_url", "job_email",
                    "job_response_ratio"]
    search_fields = ["job_id", "update_time", "crawl_platform", "refresh_date", "publish_date", "is_valid_now",
                     "company_name", "job_title", "job_department", "job_rank", "job_summary", "job_province",
                     "job_city", "job_district", "job_address", "job_work_year_min", "job_work_year_max",
                     "job_degree", "job_major", "job_language", "job_age_min", "job_age_max", "job_hours_per_day",
                     "job_days_per_week", "job_salary_min", "job_salary_max", "job_welfare", "job_type",
                     "job_advantage", "job_require", "job_responsibilities", "job_url", "job_email",
                     "job_response_ratio"]
    list_filter = ["job_id", "update_time", "crawl_platform", "refresh_date", "publish_date", "is_valid_now",
                   "company_name", "job_title", "job_department", "job_rank", "job_summary", "job_province",
                   "job_city", "job_district", "job_address", "job_work_year_min", "job_work_year_max",
                   "job_degree", "job_major", "job_language", "job_age_min", "job_age_max", "job_hours_per_day",
                   "job_days_per_week", "job_salary_min", "job_salary_max", "job_welfare", "job_type",
                   "job_advantage", "job_require", "job_responsibilities", "job_url", "job_email", "job_response_ratio"]
    readonly_fields = ["job_id", "update_time", "crawl_platform", "company_name", "job_title", "job_department",
                       "job_url", "job_email", "job_response_ratio"]
    # model_icon = 'fa fa-address-book'


xadmin.site.register(JobDetail, JobDetailAdmin)


class RecruitHistoryAdmin(object):
    list_display = ["parse_date", "summary_id", "update_time", "crawl_platform", "recruit_job_title",
                    "recruit_job_num", "recruit_company_num", "salary_min_avg", "salary_max_avg",
                    "work_year_min_mode", "work_year_max_mode", "hours_per_day_mode", "days_per_week_mode",
                    "degree_mode"]
    search_fields = ["parse_date", "summary_id", "update_time", "crawl_platform", "recruit_job_title",
                     "recruit_job_num", "recruit_company_num", "salary_min_avg", "salary_max_avg",
                     "work_year_min_mode", "work_year_max_mode", "hours_per_day_mode", "days_per_week_mode",
                     "degree_mode"]
    list_filter = ["parse_date", "summary_id", "update_time", "crawl_platform", "recruit_job_title",
                   "recruit_job_num", "recruit_company_num", "salary_min_avg", "salary_max_avg",
                   "work_year_min_mode", "work_year_max_mode", "hours_per_day_mode", "days_per_week_mode",
                   "degree_mode"]
    readonly_fields = ["parse_date", "summary_id", "update_time", "crawl_platform", "recruit_job_title"]
    # model_icon = 'fa fa-address-book'


xadmin.site.register(RecruitHistory, RecruitHistoryAdmin)


class CompanyInfoAdmin(object):
    list_display = ["update_time", "crawl_platform", "company_name", "company_type", "company_province",
                    "company_city", "company_address", "company_employ_max", "company_employ_min",
                    "company_stage", "company_industry", "company_advantage",
                    "company_invest_institution", "company_website", "company_description"]
    search_fields = ["update_time", "crawl_platform", "company_name", "company_type", "company_province",
                     "company_city", "company_address", "company_employ_max", "company_employ_min",
                     "company_stage", "company_industry", "company_advantage",
                     "company_invest_institution", "company_website", "company_description"]
    list_filter = ["update_time", "crawl_platform", "company_name", "company_type", "company_province",
                   "company_city", "company_address", "company_employ_max", "company_employ_min",
                   "company_stage", "company_industry", "company_advantage",
                   "company_invest_institution", "company_website", "company_description"]
    readonly_fields = ["update_time", "crawl_platform", "company_name", "company_type"]
    # model_icon = 'fa fa-address-book'


xadmin.site.register(CompanyInfo, CompanyInfoAdmin)


class UrlPatternAdmin(object):
    list_display = ["update_time", "platform", "category", "prefix", "parameter", "sample"]
    search_fields = ["update_time", "platform", "category", "prefix", "parameter", "sample"]
    list_filter = ["update_time", "platform", "category", "prefix", "parameter", "sample"]
    readonly_fields = []
    # model_icon = 'fa fa-address-book'


xadmin.site.register(UrlPattern, UrlPatternAdmin)
