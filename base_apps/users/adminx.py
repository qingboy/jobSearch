#-*- encoding:utf-8 -*-
# author:qingboy

import xadmin
from xadmin import views


from .models import UserProfile,VerifyCodeRecord


class VerifyCodeRecordAdmin(object):
    list_display = ["code_is_valid","mobile","email","create_time","verify_type","verify_code"]
    search_fields = ["code_is_valid","mobile","email","create_time","verify_type","verify_code"]
    list_filter = ["code_is_valid","mobile","email","create_time","verify_type","verify_code"]
    # readonly_fields = ["mobile","email","verify_code"]
    # model_icon = "fa fa-address-book"

xadmin.site.register(VerifyCodeRecord,VerifyCodeRecordAdmin)


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


class GlobalSettings(object):
    site_title = "全职搜后台管理系统"
    site_footer = "全职搜/QQ:1015158147"
    menu_style = "accordion"

xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)