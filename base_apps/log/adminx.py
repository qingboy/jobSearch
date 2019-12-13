#-*- encoding:utf-8 -*-
# author:qingboy

import xadmin
from xadmin import views


from .models import UserLog,ServerLog,CrawlLog,ProxyIP


class UserLogAdmin(object):
    list_display = ["operation_user","operation_time","operation_detail","operation_before","operation_after"]
    search_fields = ["operation_user","operation_time","operation_detail","operation_before","operation_after"]
    list_filter = ["operation_user","operation_time","operation_detail","operation_before","operation_after"]
    readonly_fields = ["operation_user","operation_time","operation_detail"]
    # model_icon = 'fa fa-address-book'

xadmin.site.register(UserLog,UserLogAdmin)


class ServerLogAdmin(object):
    list_display = ["request_user","request_user_name","request_time","request_ip","request_function","request_param","response_data"]
    search_fields = ["request_user","request_user_name","request_time","request_ip","request_function","request_param","response_data"]
    list_filter = ["request_user","request_user_name","request_time","request_ip","request_function","request_param","response_data"]
    readonly_fields = ["request_user","request_user_name","request_time","request_ip","request_function","request_param","response_data"]
    # model_icon = 'fa fa-address-book'

xadmin.site.register(ServerLog,ServerLogAdmin)


class CrawlLogAdmin(object):
    list_display = ["crawl_time","crawl_status","run_method","run_parma"]
    search_fields = ["crawl_time","crawl_status","run_method","run_parma"]
    list_filter = ["crawl_time","crawl_status","run_method","run_parma"]
    readonly_fields = ["crawl_time","crawl_status","run_method","run_parma"]
    # model_icon = 'fa fa-address-book'

xadmin.site.register(CrawlLog,CrawlLogAdmin)


class ProxyIPAdmin(object):
    list_display = ["supplier","ip","port","update_time","address","speed","proxy_type"]
    search_fields = ["supplier","ip","port","update_time","address","speed","proxy_type"]
    list_filter = ["supplier","ip","port","update_time","address","speed","proxy_type"]
    # model_icon = 'fa fa-address-book'

xadmin.site.register(ProxyIP,ProxyIPAdmin)