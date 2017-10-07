#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Logger """

import settings
import os
from datetime import datetime, timedelta
import logging

LOGGERS_INFO = {}


class Loggers(object):
    """ 格式化log """

    status_ls = {
        1: "begin",
        2: "end",
        3: "success",
        4: "fail"
    }

    def __init__(self, log_name):
        """
            log_name : logger名
        """
        self.log_name = log_name
        self.base_log_dir = settings.BASE_LOG_DIR
        self.logger = self._loginit()

    def _loginit(self):

        _date = datetime.now().strftime("%Y%m%d")
        _month = datetime.now().strftime("%Y%m")

        # 创建年月的目录
        log_dir = os.path.join(self.base_log_dir, _month)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        key = "%s_%s.log" % (self.log_name, _date)

        if key in LOGGERS_INFO:
            return LOGGERS_INFO[key]
        else:
            _logger = logging.getLogger(key)
            _logger.setLevel(logging.INFO)
            _logger.propagate = False
            log_path = os.path.join(log_dir, key)
            if not _logger.handlers:
                fh = logging.FileHandler(log_path)
                fh.setLevel(logging.INFO)
                formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
                fh.setFormatter(formatter)
                _logger.addHandler(fh)
                LOGGERS_INFO[key] = _logger

            # 删除昨日在LOGGERS_INFO中的对象
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            _key = "%s_%s.log" % (self.log_name, yesterday)
            if _key in LOGGERS_INFO:
                log = LOGGERS_INFO.pop(_key, None)
                if log:
                    for handler in log.handlers:
                        handler.close()
            return _logger

    def write(self, cmd, data=None, status=0, level=0, exc_info=None):
        """
        cmd : log行为标识
        data : 记录的数据,以dict方式
        status : 行为状态类型(例如 3 => 成功)
        level : log级别(例如 1 => warning)
        """
        data_ls = []
        if not data:
            return
        for k, v in data.iteritems():
            key_value = "%s=%s" % (k, v)
            data_ls.append(key_value)

        if status > 0:
            info = "%s:%s | %s" % (cmd, self.status_ls[status], "&".join(data_ls))
        else:
            info = "%s | %s" % (cmd, "&".join(data_ls))

        if level == 1:
            self.logger.warning(info)
        elif level == 2:
            self.logger.error(info, exc_info=exc_info)
        else:
            self.logger.info(info)
