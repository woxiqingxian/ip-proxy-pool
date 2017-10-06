#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ujson as json
import sys
import web
import settings
import db
db.init()

urls = (
    '/', 'select',
    '/all', 'select_all',
    '/delete', 'delete'
)


def start_api_server():
    sys.argv.append('0.0.0.0:%s' % settings.API_PORT)
    app = web.application(urls, globals())
    app.run()


class select(object):
    def GET(self):
        inputs = web.input()
        result = list(db.sql_handler.select(inputs.pop('count', 1), inputs))
        _resp_list = []
        for i in result:
            db.sql_handler.update(
                {'ip': i.ip, 'port': i.port},
                {'use_times': i.use_times+1}
            )
            _resp_list.append({
                "ip": i.ip,
                "port": i.port
            })
        json_result = json.dumps(_resp_list)
        return json_result


class select_all(object):
    def GET(self):
        result = db.sql_handler.select()
        _resp_list = []
        for i in result:
            _resp_list.append({
                "ip": i.ip,
                "port": i.port
            })
        json_result = json.dumps(_resp_list)

        return json_result


class delete(object):
    params = {}
    def GET(self):
        inputs = web.input()
        json_result = json.dumps(db.sql_handler.delete(inputs))
        return json_result


if __name__ == '__main__':
    sys.argv.append('0.0.0.0:5000')
    app = web.application(urls, globals())
    app.run()
