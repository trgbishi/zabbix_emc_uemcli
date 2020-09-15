#### 修改zabbix-agent.conf，使agent可以使root启动
    AllowRoot=1
#### 修改zabbix-agent.service 使agent以root启动
    service zabbix-agent status 以查看zabbix-agent.service路径
    一般为/usr/lib/systemd/system/zabbix-agent.service 
    在[Service]下添加
    User=root
    Group=root
#### 如果有特殊字符，还需要修改zabbix-agent.conf
    UnsafeUserParameters=1
#### 默认的agent执行脚本时间timeout=3，可能要对zabbix-agent.conf里的Timeout参数做修改



## 已测试：
vnxe3200
