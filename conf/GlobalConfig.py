# -*- coding:utf-8 -*-
# @Time    : 2019-5-3 20:51
# @Author  : qingboy
# @Site    :
# @File    : __init__.py.py
# @Software: PyCharm

import traceback
import os
import logging
import logging.handlers
import configparser


class GlobalConfig:
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        self.parse_config = configparser.ConfigParser()
        self.server_env = self.get_server_env()
        self.get_global_config_file()

    def get_config_value(self, section, param):
        """
        获取具体配置值
        :rtype: object
        """
        return self.parse_config.get(section, param)

    def get_global_config_file(self):
        """
        根据运行环境读取全局配置文件global_config.ini
        :return:
        """
        config_file_name = "global_config_" + self.get_server_env() + ".ini"
        global_config_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], config_file_name)
        try:
            self.parse_config.read(global_config_file)
        except Exception as e:
            print(traceback.format_exc())
            raise Exception("global_config_file:%s is not exist" % global_config_file)

    def get_server_env(self):
        """
        读取运行环境配置文件env.ini
        :return: 运行环境
        """
        env_config_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'env.ini')
        try:
            self.parse_config.read(env_config_file)
            return self.parse_config.get("env_params", "env_flag")
        except Exception as e:
            print(traceback.format_exc())
            raise Exception("global_config_file:%s is not exist" % env_config_file)

    def logger_util(self, logger_name, log_filename, logger_level_by_user=None, logger_type='one'):
        """
        通过该函数返回logger对象，已定义好日志格式，
        别的类中的调用方式：self.logger = self.logger_util(log_filename, logger_name, logger_level)
        :param logger_name: logger名称，用于区分不同logger对象
        :param log_filename: 要写入的日志文件名称, 默认文件名是相对路径：
        :param logger_level_by_user: 是否自定义日志级别，无则默认配置文件中的值
        :param logger_type: one：不需要分割；multi：需要分割，包含单进程、多进程的日志分割。
        :return: logger对象<logging.Logger object>
        """

        from . import mlogging
        logger = logging.getLogger('root')
        logger.setLevel('DEBUG')
        logger = logging.getLogger('root.' + logger_name)

        # 定义handler的输出格式
        formatter = logging.Formatter(
            '[%(asctime)s] - %(process)s - %(thread)12d - %(filename)-12s[line:%(lineno)-4d] %(levelname)-6s: %(message)s')

        # 创建一个handler，用于写入日志文件
        # 引用该脚本时需要注意日志文件存放的相对路径

        # file_log
        self.rotating_file_maxMB = self.parse_config.getint('log_params', 'rotating_file_maxMB')
        if self.parse_config.get('log_params', 'file_log_out') == 'True' and log_filename:
            if not log_filename.startswith('/'):
                log_filename = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                            self.parse_config.get('log_params', 'log_path'),
                                            log_filename)
            if logger_type == 'rotating':
                # 单进程按大小日志分割，需要使用此handler（解决存在新建日志不是apache 属性的问题）
                fh = mlogging.RotatingFileHandler_new(log_filename, 'a',
                                                      maxBytes=self.rotating_file_maxMB * 1024 * 1024, backupCount=9)
            elif logger_type == 'time-rotating':
                # 单进程按日期日志分割，需要使用此handler（解决存在新建日志不是apache 属性的问题）
                fh = mlogging.TimedRotatingFileHandler_new(log_filename, 'D', 1, 7)
                fh.suffix = "%Y%m%d.log"
            elif logger_type == 'multi-process-rotating':
                # 多进程按大小日志分割，需要使用此handler（解决存在新建日志不是apache 属性的问题）
                fh = mlogging.MultiProcessRotatingHandler_new(log_filename, 'a',
                                                              maxBytes=self.rotating_file_maxMB * 1024 * 1024,
                                                              backupCount=9)
            elif logger_type == 'multi-process-time-rotating':
                # 多进程按日期日志分割，需要使用此handler（解决存在新建日志不是apache 属性的问题）
                # 可能存在问题，暂不使用
                fh = mlogging.MultiProcessTimedRotatingFileHandler(log_filename, 'D', 1, 7)
                fh.suffix = "%Y%m%d.log"
            else:
                fh = logging.handlers.WatchedFileHandler(log_filename)

            if logger_level_by_user:
                fh_log_level = logger_level_by_user.upper()
            else:
                fh_log_level = self.parse_config.get('log_params', 'file_log_level_default').upper()
            fh.setLevel(fh_log_level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        # control_log
        # 再创建一个handler，用于输出到控制台
        if self.parse_config.getboolean('log_params', 'control_log_out'):
            ch = logging.StreamHandler()
            if logger_level_by_user:
                ch_log_level = logger_level_by_user.upper()
            else:
                ch_log_level = self.parse_config.get('log_params', 'control_log_level_default').upper()
            ch.setLevel(ch_log_level)
            ch.setFormatter(formatter)
            # 给logger添加handler
            logger.addHandler(ch)

        return logger
