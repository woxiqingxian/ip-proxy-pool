# 欢迎使用ip-proxy-pool
------
## api在线调用测试
http://ipproxypool.ingrok.wauks.cn/
<br/>
使用了ngrok服务,个人用的!请勿压测啊！

## ip-proxy-pool是什么以及为什么产生
该项目是一个ip代理池，可以获取有效的代理ip。
<br/>
这阵子在写一些爬虫，然后发现一个问题就是自己的ip经常被封锁，然后就上网找了一些ip代理，虽然可以解决我的需求，但是有很多免费的代理的ip都是比较烂的，毕竟一分钱一分货！所以就希望有一个自己的ip代理池，然后在GitHub上面也找到一些项目，但是毕竟不是自己的，自己的一些需求也不一样，所以就趁着国庆写一个啦！
该项目主要三个方面：
> * ip爬虫模块 （收集可用的代理ip）
> * 校验代理ip模块（采用多进程处理，因为校验比较耗时）
> * api服务模块 （方面外部系统调用）

## 项目依赖(本人使用mac和ubuntu)
1. 安装sqlite数据库(一般系统内置):
```
apt-get install sqlite3
```
2. 安装redis服务:
```
apt-get install redis-server
```
3. 安装requirements.txt库:
```
pip install -r requirements.txt
```

## DB配置
本项目为了最小使用化，使用的默认数据库是sqlite，然后为了数据库的拓展性，采用了sqlalchemy的ORM模型，这样就方便大家使用MySQL等数据库，而不需要改动代码。
<br/>
具体配置方法
```
    DB_CONFIG={
        # mysql配置
        "db_connect_type": "mysql",  # mysql
        "db_connect_string": 'mysql+mysqldb://root:pwd@127.0.0.1:3306/data?charset=utf8',
        "other_config": {"echo": False },
        # sqlite 配置
        # "db_connect_type": "sqlite",  # sqlite
        # "db_connect_string": 'sqlite:///' + BASE_DIR + '/data/proxy.db',
        # "other_config": {"connect_args":{'check_same_thread': False}, "echo": False },

    }
```
sqlalchemy下的DB_CONNECT_STRING参考[支持数据库](http://docs.sqlalchemy.org/en/latest/core/engines.html#supported-databases)，理论上使用这种配置方式不只是适配MySQL，sqlalchemy支持的数据库都可以。

## 如何使用
将项目目录clone到当前文件夹 -> 切换工程目录 -> 运行脚本
<br/>
```
python db.py  # 初始化db
```
比较推荐使用 supervisor 启动这些进程，这样可靠性比较高啦，工程里面有supervisor.conf可以参考！
```
python crawler.py  # 爬虫脚本
python validator.py new  # 抓取到的ip校验
python validator.py db  # 定时对数据内的ip校验
python server.py  # api服务
```
所有的模块都有系统的日志产生
目前系统默认的日志路径是在 项目 data/log 下面


## 补充说明
由于校验代理ip模块是比较耗时，所以采用了多进程处理！
<br/>
校验模块分两个，一个验证db数据，一个验证新抓取的数据。
<br/>
验证新抓取的采用了redis的阻塞式队列，尽量保证爬虫模块不会被阻塞！


## API 使用方法

### 方法一
```
GET /
```
这种模式用于查询代理ip数据，返回数据的顺序是按照速度由快到慢、使用次数由低到高。
#### 参数 

| 参数 | 类型 | 说明 |
| ----| ---- | ---- |
| types | int | 1高匿 2普匿 3透明 |
| protocol | int | 1http 2https 3http+https |
| count | int | 数量(默认为1) |
| country | int | 1 国内 2国外 |

#### 例子
```
curl http://127.0.0.1:5000/
[{"ip":"183.136.218.253","port":80}]
```

### 方法二
```
GET /all
```
####  请求参数为空
####  返回格式如上


### 方法三
```
GET /delete
```
#### 不做介绍，想要去除！因为validator.py会定期清除无用代理ip



## TODO

- [x] 基本服务接口和项目逻辑
- [ ] 改进数据库，使用redis服务
- [ ] 评分模块（根据调用次数和服务次数定期评分）

## 特别说明
- 本项目 爬虫文本分析\数据存储模块 借鉴[qiyeboy/IPProxyPool](https://github.com/qiyeboy/IPProxyPool)项目，十分感谢！

## 最后
欢迎star或fork一起改进本项目！

作者 [@woxiqingxian](https://github.com/woxiqingxian) 2017年10月06日
