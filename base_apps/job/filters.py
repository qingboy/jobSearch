# -*- coding: utf-8 -*-
__author__ = 'qingboy'

import django_filters
from django.db.models import Q

from .models import JobDetail


class JobDetailFilter(django_filters.rest_framework.FilterSet):
    job_title = django_filters.CharFilter(field_name="job_title", help_text=u"职位名称", lookup_expr="icontains")
    company_name = django_filters.CharFilter(field_name="company_name", help_text=u"公司名称", lookup_expr="icontains")
    job_summary = django_filters.CharFilter(field_name="job_summary", help_text=u"职位概述", lookup_expr="icontains")

    class Meta:
        model = JobDetail
        fields = ["job_title", "company_name", "job_summary"]
