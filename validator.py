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
import requests
import time
import sys
import ujson as json
import copy
import settings
import utils
import db
db.init()


def _detect_proxy(proxy_ip, proxy_port):
    """ 检测代理
    """
    def _request_test(test_url):
        try:
            _start = time.time()
            proxies = {
                "http": "http://%s:%s" % (proxy_ip, proxy_port),
                "https": "https://%s:%s" % (proxy_ip, proxy_port),
            }
            r = requests.get(
                url=test_url,
                headers=utils.get_html_header(),
                timeout=settings.PROXY_TEST_TIME_OUT_SECORDS,
                proxies=proxies
            )
            if r.status_code == 200:
                speed = int((time.time() - _start)*1000)
                resp_json = r.json()
                headers = resp_json['headers']
                ip = resp_json['origin']
                proxy_connection = headers.get('Proxy-Connection', None)
                if ',' in ip:
                    types = 3  # 透明
                elif proxy_connection:
                    types = 2  # 普匿
                else:
                    types = 1  # 高匿
                return True, types, speed
        except Exception as e:
            # print e
            pass
        return False, 0, 0

    protocol = 0
    http_test_url = settings.HTTP_TEST_URL
    http_result, http_types, http_speed = _request_test(http_test_url)
    protocol += 1 if http_result else 0

    https_test_url = settings.HTTPS_TEST_URL
    https_result, https_types, https_speed = _request_test(https_test_url)
    protocol += 2 if https_result else 0

    types = 0
    speed = 0
    if protocol == 1:
        types = http_types
        speed = http_speed
    elif protocol == 2:
        types = https_types
        speed = https_speed
    elif protocol == 3:
        types = http_types
        speed = http_speed
    else:
        return None

    proxy_info = {
        "ip": proxy_ip,
        "port": proxy_port,
        "protocol": protocol,
        "types": types,
        "speed": speed,
    }
    return proxy_info


def _validator_proxy(proxy_list, _type):
    from db import SqlHandler
    sql_handler = SqlHandler()  # 进程自己生成！
    for proxy in proxy_list:
        ip = proxy['ip']
        port = proxy['port']
        proxy_info = _detect_proxy(ip, port)
        if proxy_info and _type == "db":
            # 更新
            sql_handler.update(
                {'ip': ip, 'port': port},
                {'speed': proxy_info['speed'], 'types': proxy_info['types'], 'protocol': proxy_info['protocol']}
            )
        elif proxy_info and _type == "new":
            result = sql_handler.select(count=1, conditions={"ip": ip, "port":port })
            if result:
                continue
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
