# -*- encoding:utf-8 -*-
# author:qingboy

from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery('celery_task')
app.config_from_object('celery_task.config')
