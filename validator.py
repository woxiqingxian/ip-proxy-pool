#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    python validator.py db
    python validator.py new
    使用脚本跑
    校验模块
        1: 校验数据库
        2: 校验新加入
    采用多线程
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from multiprocessing import Process
from logger import Loggers
import sys
import ujson as json
import copy
import settings
import utils
import db
db.init()


def _validator_proxy(proxy_list, _type):
    from db import SqlHandler
    sql_handler = SqlHandler()  # 进程自己生成！
    for proxy in proxy_list:
        ip = proxy['ip']
        port = proxy['port']
        proxy_info = utils.detect_proxy(ip, port)
        if proxy_info and _type == "db":
            # 更新
            sql_handler.update(
                {'ip': ip, 'port': port},
                {'speed': proxy_info['speed'], 'types': proxy_info['types'], 'protocol': proxy_info['protocol']}
            )
        elif proxy_info and _type == "new":
            area = utils.get_address_from_ip(ip)
            new_params = {
                'ip': ip,
                'port': port,
                'protocol': proxy_info['protocol'],
                'area': area,
                'country': 1 if any(i in area for i in settings.CHINA_AREA_LIST) else 2,
                'speed': proxy_info['speed'],
                'types': proxy_info['types'],
            }
            sql_handler.insert(new_params)
        elif not proxy_info and _type == "db":
            # 删除
            sql_handler.delete({'ip': ip, 'port': port})
        else:
            # 不处理
            pass

        if proxy_info:
            log_params = copy.deepcopy(proxy_info)
            log_params['msg'] = "success~~~~"
        else:
            log_params = {"msg": "fail!!", 'ip': ip, 'port': port}
        Loggers('validator').write('_validator_proxy', log_params)

    return


def validator_proxy(proxy_list, _type):
    """ _type "db", "new"
    """
    proxy_list_num = len(proxy_list)
    process_num = settings.PROXY_TEST_PROCESS_NUM
    # print "总量", proxy_list_num
    # print "进程数", process_num
    average_num = int((proxy_list_num+process_num-1)/process_num)
    # print "每个进程处理数量", average_num
    process_list = list()
    for index in range(process_num):
        # print proxy_list_num, index*average_num, (index+1)*average_num
        _proxy_list = proxy_list[index*average_num: (index+1)*average_num]
        if not _proxy_list:
            continue
        process_list.append(
            Process(
                target=_validator_proxy,
                args=(_proxy_list, _type, )
            )
        )

    for _process in process_list:
        _process.start()

    for _process in process_list:
        _process.join()
    return


def db_validator():
    # 更新db数据
    result = db.sql_handler.select()
    proxy_list = [{'ip': i.ip, 'port': i.port} for i in result]
    validator_proxy(proxy_list, "db")


def new_validator():
    # db.redis.rpush(
    #     constants.WIN_DELIVERY_QUEUE,
    #     "%s,%s,%s" % (confirm_type, sid, aid)
    # )
    # data = db.redis.blpop(constants.WIN_DELIVERY_QUEUE)
    # if not data:
    #     continue
    # comfirm_type, sid, aid = data[1].split(',')
    while True:
        data = db.redis.blpop(settings.NEW_VALIDATOR_QUEUE)
        if not data:
            continue
        proxy_list = json.loads(data[1])
        validator_proxy(proxy_list, "new")


def run():
    db_validator()
    sched = BlockingScheduler()
    sched.add_job(db_validator, 'interval', minutes=5)  # 每5分钟更新一次
    sched.start()


if __name__ == "__main__":
    if len(sys.argv) == 2 and str(sys.argv[1]) == "new":
        new_validator()
    else:
        run()
