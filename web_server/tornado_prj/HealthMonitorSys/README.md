Ctrl+shift+g:find in path
验证用户是否登录的装饰器                                                          
from tornado.web import authenticated

aiofiles:异步读写文件，主要用于上传图片

杀死指定端口进程：netstat -ano|findstr "8008"
taskkill /f /t /im "pid"

mysql -uroot -p123456
启动后台服务
开启Redis服务：redis-server.exe(E:\taylen_software\Redis-x64-3.0.504)
启动一个client，redis-cli.exe
> keys *
> get 键（查看键所对应的的值）
启动PHPstarrt，开启Nginx服务

1.1
所应用到的技术点:
关系型数据库:mysql
后端框架:tornado
数据库驱动:pymysql
数据库ORM:peewee
服务端websocket通信:sockjs-tornado
客户端websocket通信:sockjs-client
前端框架:bootstrap
可视化图标:pyechars

整体项目，采用MTV思想
M:模型(models),用来和数据库交互(增删改查)
T:模板(templates),负责把页面展示给用户
V:视图(views),负责业务逻辑处理，适当时候调用models、templates

1.2
分析项目目录：

|---- server.py # 入口启动文件，负责启动服务
|---- apps # 应用包，存放MV
|---- templates # 模板文件，存放T
|---- static # 静态文件目录（css、js、图片）
|---- tools # 工具包映射数据库创建表、测试工具等）
|---- HealthMonitor
|-------- handler.py # 基础视图（目录信息、数据库等）
|-------- settings.py # 配置信息（目录信息、数据库等）
|-------- urls.py # 基础路由视图映射配置文件（配置路由规则）
|-------- models # 基础模型包（存放基础模型模块）
|-------- templates # 模板目录（存放html模板）


二、数据库
2.1设计用户模块

2.2设计ECG检测报告模块
编号       id            int         自增 主键
添加时间    add_time      datatime 
用户id     user_id       int         外键
平均心率    heartRateAvg  smallint
最快心率    heartRateMax  smallint    
最慢心律    heartRateMin  smallint
心电数据    ecg_data      longtext
心率数据    heartRate_data longtext

解决心电数据存储过程中报错：data too long for column 'ecg_data' at row 1
修改my.ini文件：将sql-mode=STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION注释掉

设计心电数据统计模块
分析字段：
    编号 id 大整型 主键
    心电数据 ecg_data 小数类型 允许为空
    心率 heart_rate 整数类型 允许为空
    创建日期 create_date 日期类型
    创建时间 create_time 时间类型
    创建日期时间 create_dt 日期时间类型

2.1
建立websocket服务端

1.建立连接
2.发送消息，主动把消息推送给所有连接着服务端的客户端
3.关闭连接

sockjs-tornado



websocketd --port=8009 --address=127.0.0.1 python ws_server.py