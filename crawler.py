#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    python crawler.py
    网站爬虫模块
    使用脚本跑
"""

import ujson as json
import settings
import re
import base64
from proxy_request import ApiRequest
from apscheduler.schedulers.blocking import BlockingScheduler
from lxml import etree
import db
db.init()


class HtmlParser(object):

    def __init__(self, html_content, parser):
        """
        :param html_content: html内容
        :param type: 解析方式
        """
        self.html_content = html_content
        self.parser = parser

    def parse(self):
        if self.parser['type'] == 'xpath':
            return self._xpath_praser()
        elif self.parser['type'] == 'regular':
            return self._regular_praser()
        elif self.parser['type'] == 'module':
            return getattr(self, self.parser['moduleName'], None)()
        else:
            return None

    def _xpath_praser(self):
        """ 针对xpath方式进行解析
        """
        proxy_list = []
        root = etree.HTML(self.html_content)
        proxys = root.xpath(self.parser['pattern'])
        for proxy in proxys:
            try:
                ip = proxy.xpath(self.parser['position']['ip'])[0].text
                port = proxy.xpath(self.parser['position']['port'])[0].text
            except Exception:
                continue
            proxy = {
                'ip': ip,
                'port': port,
            }
            proxy_list.append(proxy)
        return proxy_list

    def _regular_praser(self):
        ''' 针对正则表达式进行解析
        '''
        proxy_list = []
        pattern = re.compile(self.parser['pattern'])
        matchs = pattern.findall(self.html_content)
        if not matchs:
            return proxy_list
        for match in matchs:
            try:
                ip = match[self.parser['position']['ip']]
                port = match[self.parser['position']['port']]
            except Exception:
                continue
            proxy = {
                'ip': ip,
                'port': port,
            }
            proxy_list.append(proxy)
        return proxy_list

    def _cnproxy_praser(self):
        proxy_list = self._regular_praser()
        chardict = {'v': '3', 'm': '4', 'a': '2', 'l': '9', 'q': '0', 'b': '5', 'i': '7', 'w': '6', 'r': '8', 'c': '1'}

        for proxy in proxy_list:
            port = proxy['port']
            new_port = ''
            for i in range(len(port)):
                if port[i] != '+':
                    new_port += chardict[port[i]]
            proxy['port'] = new_port
        return proxy_list

    # def _proxy_listPraser(self):
    #     proxy_list = []
    #     pattern = re.compile(self.parser['pattern'])
    #     matchs = pattern.findall(self.html_content)
    #     if not matchs:
    #         return proxy_list

    #     for match in matchs:
    #         try:
    #             ip_port = base64.b64decode(match.replace("Proxy('", "").replace("')", ""))
    #             ip = ip_port.split(':')[0]
    #             port = ip_port.split(':')[1]
    #         except Exception:
    #             continue
    #         proxy = {
    #             'ip': ip,
    #             'port': port,
    #         }
    #         proxy_list.append(proxy)
    #     return proxy_list


class Crawler(object):

    def __init__(self):
        self.crawler_web_list = settings.CRAWLER_WEB_LIST

    def _crawler_web(self, web_config):
        all_proxy_list = []
        all_proxy_set = set([])

        url_list = web_config['url_list']
        parser_config = web_config['parser_config']
        for url in url_list:
            resp_obj = ApiRequest().request(url)
            if not resp_obj:
                continue
            # 获取ip
            _proxy_list = HtmlParser(resp_obj.content, parser_config).parse()
            _proxy_set = set(["%s:%s" % (_proxy['ip'], _proxy['port']) for _proxy in _proxy_list])
            all_proxy_list += _proxy_list
            all_proxy_set = all_proxy_set.union(_proxy_set)
            if len(all_proxy_set) >= 100:
                db.redis.rpush(
                    settings.NEW_VALIDATOR_QUEUE,
                    json.dumps([{"ip": i.split(":")[0], "port": i.split(":")[1]} for i in all_proxy_set])
                )
                all_proxy_list = []
                all_proxy_set = set([])

        return

    def run(self):
        for web_config in self.crawler_web_list:
            self._crawler_web(web_config)
        return


def main():
    Crawler().run()


def run():
    main()
    sched = BlockingScheduler()
    sched.add_job(main, 'interval', minutes=10)  # 每10分钟抓取一次
    sched.start()


if __name__ == "__main__":
    run()
