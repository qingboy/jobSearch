# -*- encoding:utf-8 -*-
# author:qingboy
from conf import GlobalConfig

global_config = GlobalConfig.GlobalConfig()

BROKER_URL = global_config.get_config_value("celery_redis_params", "broker_redis_url")  # Broker配置，使用Redis作为消息中间件

BROKER_POOL_LIMIT = None

CELERY_RESULT_BACKEND = global_config.get_config_value("celery_redis_params", "result_redis_url")  # BACKEND配置，这里使用redis

CELERY_RESULT_SERIALIZER = 'json'  # 结果序列化方案

CELERY_ACCEPT_CONTENT = ['json']

CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24  # 任务过期时间

CELERY_TIMEZONE = 'Asia/Shanghai'  # 时区配置

CELERY_ENABLE_UTC = True

CELERYD_MAX_TASKS_PER_CHILD = 10

from celery import platforms

# 允许root 用户运行celery
platforms.C_FORCE_ROOT = True

CELERY_IMPORTS = (  # 指定导入的任务模块,可以指定多个
    'celery_task.tasks',
)

from celery_task import app
from celery.schedules import crontab

app.conf.beat_schedule = {
    'job_daily_summary': {
        'task': 'celery_task.tasks.job_daily_summary',
        'schedule': crontab(minute='30', hour='23', day_of_week='2,4,0'),
    },
    "start_parse_xmrc": {
        'task': 'celery_task.tasks.start_parse_xmrc',
        'schedule': crontab(minute='20', hour='0', day_of_week='1,3,5'),
    }
}
