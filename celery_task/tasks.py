# -*- coding:utf-8 -*-
# @author:qingboy

from __future__ import absolute_import, unicode_literals

import json
import os

from datetime import datetime
import pandas as pd
import numpy as np
import pymysql
from scipy import stats
from sqlalchemy import create_engine

from celery_task import app

from conf import GlobalConfig

global_config = GlobalConfig.GlobalConfig()
logger = global_config.logger_util("celery_task", "celery_task.log")

from utils.redis_util import init_cache_redis_conn
cache_redis_conn = init_cache_redis_conn(1)


@app.task
def start_parse_xmrc():
    command = "/usr/bin/curl http://localhost:6800/schedule.json -d project=dataCollection -d spider=xmrc"
    jobid = json.loads(str(os.popen(command).read()))
    logger.info(command)
    logger.info(jobid["jobid"])
    return jobid["jobid"]


@app.task
def stop_parse_xmrc(jobid):
    command = "/usr/bin/curl http://localhost:6800/cancel.json -d project=dataCollection -d job=" + jobid
    status = json.loads(str(os.popen(command).read()))
    logger.info(command)
    logger.info(status)


@app.task
def job_daily_summary():
    """
    定时将岗位明细信息表job_jobdetail汇总统计写入岗位历史信息表job_recruithistory
    """
    conn = pymysql.connect(host=global_config.get_config_value("db_params", "host"),
                           port=global_config.get_config_value("db_params", "port"),
                           user=global_config.get_config_value("db_params", "user"),
                           passwd=global_config.get_config_value("db_params", "password"),
                           db=global_config.get_config_value("db_params", "name"),
                           charset="utf8")
    sql = "SELECT update_time,crawl_platform,job_title,company_name," \
          "job_work_year_min,job_work_year_max,job_degree,job_age_min," \
          "job_age_max,job_hours_per_day,job_days_per_week,job_salary_min," \
          "job_salary_max,job_degree FROM job_jobdetail WHERE is_valid_now = TRUE;"
    job_detail_df = pd.read_sql(sql, con=conn)
    logger.info("job detail data set:%s", job_detail_df.shape)
    if not job_detail_df.empty:
        # 以更新日期@招聘平台@岗位名称作为汇总key
        job_detail_df["summary_id"] = job_detail_df["update_time"].apply(lambda x: x.strftime("%Y-%m-%d")) + "@" + \
                                      job_detail_df["crawl_platform"] + "@" + job_detail_df["job_title"]
        # 汇总算法：
        # 计数：岗位名称
        # 去重计数：公司名称
        # 去0均值：岗位薪酬上/下限，工作经验上/下限
        # 众数：天工作时长，周工作天数
        job_summary_tmp_df = (job_detail_df.groupby("summary_id").agg(
            {
                "job_title": ["count"],
                "company_name": [lambda x: np.count_nonzero(np.unique(x))],
                "job_salary_min": [lambda x: np.sum(x) / np.count_nonzero(x)],
                "job_salary_max": [lambda x: np.sum(x) / np.count_nonzero(x)],
                "job_work_year_min": [lambda x: np.sum(x) / np.count_nonzero(x)],
                "job_work_year_max": [lambda x: np.sum(x) / np.count_nonzero(x)],
                "job_hours_per_day": [lambda x: stats.mode(x)[0]],
                "job_days_per_week": [lambda x: stats.mode(x)[0]],
            }))
        job_summary_df = pd.DataFrame(job_summary_tmp_df.values)
        job_summary_df["summary_id"] = job_summary_tmp_df.index
        job_summary_df["update_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 由汇总key拆分出更新日期、招聘平台、岗位名称
        job_summary_df["parse_date"] = job_summary_df["summary_id"].str.split("@", expand=True)[0]
        job_summary_df["crawl_platform"] = job_summary_df["summary_id"].str.split("@", expand=True)[1]
        job_summary_df["recruit_job_title"] = job_summary_df["summary_id"].str.split("@", expand=True)[2]
        job_summary_df = job_summary_df.rename(
            columns={0: "recruit_job_num", 1: "recruit_company_num", 2: "salary_min_avg",
                     3: "salary_max_avg", 4: "work_year_min_mode", 5: "work_year_max_mode",
                     6: "hours_per_day_mode", 7: "days_per_week_mode"})

        job_summary_df.fillna(0)
        # 创建pandas数据库连接，写入数据库
        con = create_engine("mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8"
                            % (global_config.get_config_value("db_params", "user"),
                               global_config.get_config_value("db_params", "password"),
                               global_config.get_config_value("db_params", "host"),
                               global_config.get_config_value("db_params", "port"),
                               global_config.get_config_value("db_params", "name")))
        job_summary_df.to_sql(name="job_recruithistory", con=con, if_exists="append", chunksize=5000, index=False,
                              index_label="summary_id")

        # 清空job_jobdetail表
        cursor = conn.cursor()
        cursor.execute("TRUNCATE job_jobdetail;")
        conn.commit()
        cursor.close()
        conn.close()
        # 获取新的岗位信息后清空redis所有缓存
        cache_redis_conn.flushall()
