#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 sql操作的基类
'''

import settings
import redis as c_redis
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, VARCHAR
from sqlalchemy import UniqueConstraint
from sqlalchemy import create_engine

redis = None
sql_handler = None
BaseModel = declarative_base()


class ISqlHandler(object):
    params = {
        'ip': None, 'port': None,
        'types': None, 'protocol': None,
        'country': None, 'area': None,
        'speed': None, 'score': None,
        'update_time': None, 'create_time': None,
        'use_times': None,
    }

    def init_db(self):
        raise NotImplemented

    def drop_db(self):
        raise NotImplemented

    def insert(self, value=None):
        raise NotImplemented

    def delete(self, conditions=None):
        raise NotImplemented

    def update(self, conditions=None, value=None):
        raise NotImplemented

    def select(self, count=None, conditions=None):
        raise NotImplemented


class Proxy(BaseModel):
    __tablename__ = 'proxys'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(VARCHAR(16), nullable=False)
    port = Column(Integer, nullable=False)
    types = Column(Integer, nullable=False, default=0)  # 1高匿 2普匿 3透明
    protocol = Column(Integer, nullable=False, default=0)  # 0无 1http 2https 3http+https
    country = Column(Integer, nullable=False, default=0)  # 1 国内 2国外
    area = Column(VARCHAR(100), nullable=False, default="")
    speed = Column(Integer, nullable=False, default=0)  # 毫秒
    score = Column(Integer, nullable=False, default=settings.DEFAULT_SCORE)
    use_times = Column(Integer, nullable=False, default=0)  # 使用次数
    # update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    create_time = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('ip', 'port', name='ip_port'),  # 联合唯一索引
    )


class SqlHandler(ISqlHandler):
    params = {
        'ip': Proxy.ip, 'port': Proxy.port,
        'types': Proxy.types, 'protocol': Proxy.protocol,
        'country': Proxy.country, 'area': Proxy.area,
        'score': Proxy.score, 'speed': Proxy.speed,
        'update_time': Proxy.update_time, 'create_time': Proxy.create_time,
        'use_times': Proxy.use_times
    }

    def __init__(self):
        _db_connect_string = settings.DB_CONFIG['db_connect_string']
        _other_config = settings.DB_CONFIG['other_config']
        self.engine = create_engine(
            _db_connect_string, **_other_config)
        DB_Session = sessionmaker(bind=self.engine)
        self.session = DB_Session()

    def init_db(self):
        BaseModel.metadata.create_all(self.engine)

    def drop_db(self):
        BaseModel.metadata.drop_all(self.engine)

    def insert(self, value):
        try:
            proxy = Proxy(
                ip=value['ip'],
                port=value['port'],
                types=value['types'],
                protocol=value['protocol'],
                country=value['country'],
                area=value['area'],
                speed=value['speed']
            )
            self.session.add(proxy)
            self.session.commit()
        except Exception as e:
            print e
            pass

    def delete(self, conditions=None):
        if conditions:
            conditon_list = []
            for key in list(conditions.keys()):
                if self.params.get(key, None):
                    conditon_list.append(
                        self.params.get(key) == conditions.get(key))
            conditions = conditon_list
            query = self.session.query(Proxy)
            for condition in conditions:
                query = query.filter(condition)
            delete_num = query.delete()
            self.session.commit()
        else:
            delete_num = 0
        return {'delete_num', delete_num}

    def update(self, conditions=None, value=None):
        '''
        conditions的格式是个字典。类似self.params
        :param conditions:
        :param value:也是个字典：{'ip':192.168.0.1}
        :return:
        '''
        if conditions and value:
            conditon_list = []
            for key in list(conditions.keys()):
                if self.params.get(key, None):
                    conditon_list.append(
                        self.params.get(key) == conditions.get(key))
            conditions = conditon_list
            query = self.session.query(Proxy)
            for condition in conditions:
                query = query.filter(condition)
            updatevalue = {}
            for key in list(value.keys()):
                if self.params.get(key, None):
                    updatevalue[self.params.get(key, None)] = value.get(key)
            update_num = query.update(updatevalue)
            self.session.commit()
        else:
            update_num = 0
        return {'update_num': update_num}

    def select(self, count=None, conditions=None):
        '''
        conditions的格式是个字典。类似self.params
        :param count:
        :param conditions:
        :return:
        '''
        if conditions:
            conditon_list = []
            for key in list(conditions.keys()):
                if self.params.get(key, None):
                    conditon_list.append(
                        self.params.get(key) == conditions.get(key))
            conditions = conditon_list
        else:
            conditions = []

        # query = self.session.query(Proxy.ip, Proxy.port, Proxy.score)
        query = self.session.query(Proxy)
        if len(conditions) > 0:
            for condition in conditions:
                query = query.filter(condition)
        if count:
            return query.order_by(Proxy.use_times, Proxy.score.desc(), Proxy.speed).limit(count).all()
        else:
            return query.order_by(Proxy.use_times, Proxy.score.desc(), Proxy.speed).all()
        return

    def close(self):
        pass


def init():
    global sql_handler, redis
    sql_handler = SqlHandler()
    redis = c_redis.Redis(
        connection_pool=c_redis.ConnectionPool(**settings.REDIS_CONFIG))


if __name__ == '__main__':
    sql_handler = SqlHandler()
    sql_handler.init_db()
    # proxy = {'ip': '192.168.1.1', 'port': 80, 'type': 0, 'protocol': 0, 'country': u'中国', 'area': u'广州', 'speed': 1123, 'types': ''}
    # sql_handler.insert(proxy)
    # result = sql_handler.select()
    # print len(result)
    # ip_port_set = set()
    # for i in result:
    #     print "%s:%s %s %s" % (i.ip, i.port, i.create_time, i.update_time)
    #     ip_port_set.add("%s:%s" % (i.ip, i.port))
    # print len(ip_port_set)
        # print type(i.ip), i.ip
        # print type(i.port), i.port
        # print type(i.speed), i.speed
        # print type(i.create_time), i.create_time
        # print type(i.update_time), i.update_time

    # import time
    # time.sleep(2.312)
    # sql_handler.update({'ip': '192.168.1.1', 'port': 80}, {'speed': 100})
    # result = sql_handler.select()
    # print type(result[0].speed), result[0].speed
    # print type(result[0].create_time), result[0].create_time
    # print type(result[0].update_time), result[0].update_time

    # sql_handler.drop_db()
    # result = sql_handler.select()
    # print result
