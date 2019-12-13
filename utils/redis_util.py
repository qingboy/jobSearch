# -*- coding:utf-8 -*-
# @Time    : 2019-4-16 21:53
# @Author  : qingboy
# @Site    :
# @File    : job_daily_summary.py
# @Software: PyCharm

import redis
from conf import GlobalConfig
global_config = GlobalConfig.GlobalConfig()
cache_redis_host = global_config.get_config_value("cache_redis_params", "cache_redis_host")
cache_redis_port = global_config.get_config_value("cache_redis_params", "cache_redis_port")
cache_redis_db = global_config.get_config_value("cache_redis_params", "cache_redis_db")
cache_redis_password = global_config.get_config_value("cache_redis_params", "cache_redis_password")


def init_cache_redis_conn(db):
    redis_pool = redis.ConnectionPool(host=cache_redis_host, port=cache_redis_port, db=db,
                                      password=cache_redis_password, decode_responses=True)
    cache_redis_conn = redis.StrictRedis(connection_pool=redis_pool, decode_responses=True)
    return cache_redis_conn
