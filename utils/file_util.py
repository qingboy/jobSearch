# -*- coding:utf-8 -*-
# @Time    : 2019-5-3 20:51
# @Author  : qingboy
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm

import os
import pwd


def get_owner(file_path=None):
    if file_path is not None:
        if not os.path.exists(file_path):
            print("file path [%s] not exist!" % file_path)
            return ""
        stat = os.lstat(file_path)
        uid = stat.st_uid
    else:
        uid = os.getuid()
    pw = pwd.getpwuid(uid)
    return pw.pw_name


def chown_apache(file_path):
    if not os.path.exists(file_path):
        print("file path [%s] not exist!" % file_path)
        return 1
    file_owner = get_owner(file_path)

    if file_owner != "apache":
        current_owner = get_owner()
        print("file_owner, current_owner: %s, %s" % (file_owner, current_owner))
        if current_owner == "root":
            pw = pwd.getpwnam("apache")
            os.chown(file_path, pw.pw_uid, pw.pw_gid)
        else:
            print("chown: changing ownership of `%s': Operation not permitted" % file_path)
            return 1
    return 0
