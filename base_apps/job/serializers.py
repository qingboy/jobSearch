# -*- coding: utf-8 -*-
# __author__ = 'qingboy'

from rest_framework import serializers

from job.models import JobDetail


class JobDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDetail
        fields = ["company_name", "job_title", "job_department", "job_address",
                  "job_work_year_min", "job_degree", "job_major", "job_language",
                  "job_hours_per_day", "job_days_per_week", "job_salary_min",
                  "job_salary_max", "job_welfare", "job_summary", "job_url"]
