# 欢迎使用ip-proxy-pool
------
## ip-proxy-pool是什么以及为什么产生
该项目是一个ip代理池，可以通过结果获取有效的代理ip。
<br/>
这阵子在写一些爬虫，然后发现一个问题就是自己的ip经常被封锁，然后就上网找了一些ip代理，虽然可以解决我的需求，但是有很多免费的代理的ip都是比较烂的，毕竟一分钱一分货！所以就希望有一个自己的ip代理池，然后在GitHub上面也找到一些项目，但是毕竟不是自己的，自己的一些需求也不一样，所以就趁着国庆写一个啦！
该项目主要三个方面：
> * ip爬虫模块 （收集可用的代理ip）
> * 校验代理ip模块（采用多进程处理，因为校验比较耗时）
> * api服务模块 （方面外部系统调用）

## 项目依赖(本人使用mac和ubuntu)

1.安装sqlite数据库(一般系统内置):
```python
apt-get install sqlite3
```
2.安装requirements.txt库:
```python
pip install -r requirements.txt
```

## DB配置
本项目为了最小使用化，使用的默认数据库是sqlite，然后为了数据库的拓展性，采用了sqlalchemy的ORM模型，这样就方便大家使用MySQL，MongoDB数据库等，而不需要改动代码。
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
        # "other_config": {'check_same_thread': False, "echo": False },

    }
```
sqlalchemy下的DB_CONNECT_STRING参考[支持数据库](http://docs.sqlalchemy.org/en/latest/core/engines.html#supported-databases)，理论上使用这种配置方式不只是适配MySQL，sqlalchemy支持的数据库都可以，但是仅仅测试过MySQL。
<br/>
* 有感兴趣的朋友，可以将Redis的实现方式添加进来。

## 如何使用
将项目目录clone到当前文件夹 -> 切换工程目录 -> 运行脚本
<br/>
比较推荐使用 supervisor 启动这些进程，这样可靠性比较高啦~
```
python crawler.py  # 爬虫脚本
python validator.py new  # 抓取到的ip校验
python validator.py db  # 定时对数据内的ip校验
python server.py  # api服务
```
所有的模块都有系统的日志产生
目前系统默认的日志路径是在 项目 data/log 下面

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
| area | str | 地区 |

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



### TODO

- [x] 基本服务接口和项目逻辑
- [ ] 改进数据库，使用redis服务
- [ ] 评分模块（根据调用次数和服务次数定期评分）

------
欢迎star或fork一起改进本项目！

作者 [@woxiqingxian](https://github.com/woxiqingxian)
<br/>
2017年10月06日
