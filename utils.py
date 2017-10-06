#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time
import IP
import random
import settings


def get_address_from_ip(ip, _type=0):
    """
        获取ip地址 返回格式
        _type = 0  中国广东广州
        _type = 1  中国\t广东\t广州
        _type = 2 [u'中国', u'广东', u'广州']
    """
    ip_address = IP.find(ip)
    if _type == 0:
        ip_address = ''.join(ip_address.split('\t'))
    elif _type == 1:
        ip_address = ip_address
    elif _type == 2:
        ip_address = ip_address.split('\t')
    else:
        ip_address = ''.join(ip_address.split('\t'))
    return ip_address


def get_html_header():
    return {
        'User-Agent': random.choice(settings.USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
    }


def detect_proxy(proxy_ip, proxy_port):
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
                headers=get_html_header(),
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


if __name__ == "__main__":
    proxy_list = [{'ip': '212.237.61.174', 'port': '8080'}, {'ip': '213.169.48.14', 'port': '53281'}, {'ip': '181.214.224.96', 'port': '3128'}, {'ip': '176.194.252.118', 'port': '8081'}, {'ip': '79.111.169.9', 'port': '53281'}, {'ip': '50.234.147.30', 'port': '80'}, {'ip': '192.208.184.134', 'port': '8080'}, {'ip': '212.56.203.74', 'port': '8080'}, {'ip': '198.50.240.19', 'port': '8080'}, {'ip': '79.120.74.248', 'port': '8080'}, {'ip': '46.172.4.125', 'port': '8081'}, {'ip': '207.144.127.122', 'port': '3128'}, {'ip': '192.95.21.109', 'port': '80'}, {'ip': '86.57.240.64', 'port': '8080'}, {'ip': '104.198.227.184', 'port': '80'}, {'ip': '185.64.220.113', 'port': '65103'}, {'ip': '67.225.218.166', 'port': '80'}, {'ip': '67.225.218.190', 'port': '80'}, {'ip': '208.74.120.58', 'port': '3128'}, {'ip': '199.96.227.198', 'port': '3128'}, {'ip': '78.36.39.220', 'port': '8080'}, {'ip': '194.226.35.88', 'port': '4444'}, {'ip': '216.87.176.99', 'port': '80'}, {'ip': '46.235.217.22', 'port': '3128'}, {'ip': '104.236.27.71', 'port': '8080'}, {'ip': '194.42.195.158', 'port': '53281'}, {'ip': '5.1.27.124', 'port': '53281'}, {'ip': '104.236.27.71', 'port': '80'}, {'ip': '208.74.120.59', 'port': '3128'}, {'ip': '194.226.35.86', 'port': '4444'}, {'ip': '91.93.132.138', 'port': '3128'}, {'ip': '199.96.227.198', 'port': '80'}, {'ip': '91.223.64.179', 'port': '80'}, {'ip': '107.16.213.250', 'port': '8080'}, {'ip': '203.74.4.3', 'port': '80'}, {'ip': '91.228.89.29', 'port': '3128'}, {'ip': '216.100.88.228', 'port': '8080'}, {'ip': '216.100.88.229', 'port': '8080'}, {'ip': '83.169.244.158', 'port': '8080'}, {'ip': '203.74.4.7', 'port': '80'}, {'ip': '203.74.4.5', 'port': '80'}, {'ip': '203.74.4.0', 'port': '80'}, {'ip': '203.74.4.6', 'port': '80'}, {'ip': '203.74.4.1', 'port': '80'}, {'ip': '203.74.4.2', 'port': '80'}, {'ip': '52.161.111.193', 'port': '80'}, {'ip': '183.136.218.253', 'port': '80'}, {'ip': '213.136.105.62', 'port': '3128'}, {'ip': '46.191.237.63', 'port': '65309'}, {'ip': '185.65.186.192', 'port': '8080'}, {'ip': '195.154.77.130', 'port': '3128'}, {'ip': '212.47.252.49', 'port': '3128'}, {'ip': '185.52.2.138', 'port': '3128'}, {'ip': '185.42.221.246', 'port': '80'}, {'ip': '77.73.241.154', 'port': '80'}, {'ip': '213.202.212.17', 'port': '8888'}, {'ip': '5.189.143.77', 'port': '3128'}, {'ip': '212.237.11.87', 'port': '80'}, {'ip': '212.237.27.44', 'port': '8080'}, {'ip': '212.237.61.174', 'port': '3128'}, {'ip': '178.238.226.201', 'port': '3128'}, {'ip': '94.177.175.232', 'port': '80'}, {'ip': '94.177.203.243', 'port': '3128'}, {'ip': '178.62.25.153', 'port': '3128'}, {'ip': '188.165.194.110', 'port': '8888'}, {'ip': '77.239.133.146', 'port': '80'}, {'ip': '5.8.8.85', 'port': '80'}, {'ip': '80.211.237.231', 'port': '8080'}, {'ip': '5.8.8.98', 'port': '80'}, {'ip': '82.202.212.174', 'port': '80'}, {'ip': '194.226.35.84', 'port': '4444'}, {'ip': '94.177.175.232', 'port': '3128'}, {'ip': '84.121.23.149', 'port': '80'}, {'ip': '77.239.133.146', 'port': '3128'}, {'ip': '84.121.242.150', 'port': '80'}, {'ip': '94.177.175.232', 'port': '8080'}, {'ip': '176.99.70.198', 'port': '8080'}, {'ip': '82.202.226.203', 'port': '80'}, {'ip': '85.26.146.169', 'port': '80'}, {'ip': '195.190.124.202', 'port': '8080'}, {'ip': '178.212.43.163', 'port': '8080'}, {'ip': '188.43.15.105', 'port': '9090'}, {'ip': '104.236.27.71', 'port': '3128'}, {'ip': '193.93.216.95', 'port': '8080'}, {'ip': '5.152.158.4', 'port': '8080'}, {'ip': '185.107.143.99', 'port': '8080'}, {'ip': '46.164.141.45', 'port': '8081'}, {'ip': '62.81.245.12', 'port': '3128'}, {'ip': '195.230.16.88', 'port': '9090'}, {'ip': '85.192.17.77', 'port': '8081'}, {'ip': '178.124.139.76', 'port': '80'}, {'ip': '199.195.253.124', 'port': '3128'}, {'ip': '198.98.61.187', 'port': '3128'}, {'ip': '87.244.35.22', 'port': '8080'}, {'ip': '199.195.253.124', 'port': '03128'}, {'ip': '188.211.226.55', 'port': '53281'}, {'ip': '193.227.49.83', 'port': '8080'}, {'ip': '194.183.173.72', 'port': '8080'}, {'ip': '83.69.110.218', 'port': '8081'}, {'ip': '54.175.112.39', 'port': '3128'}]
    for proxy in proxy_list:
        print detect_proxy(proxy['ip'], proxy['port'])