通过uemcli取emc vnxe3200数据，其它型号未测试
目前不支持通过zabbix server或agent直接执行脚本（即通过外部检查或zabbix客户端），报错为：
Operation failed. Error code: 0x1000002
The system encountered an unexpected error. Record the error code and go to the EMC Online Support website for all your support options. (Error Code:0x1000002)

目前只能通过linux的系统指令定时执行

执行步骤：
crontab -e 以添加任务（注意修改脚本路径及参数）
*/15 *  *  *  *  python emc_uemcli_script.py --device_ip {$ip} --device_user {$user} --device_password {$pass} --zabbix_host_name {$zabbix host name}  --discover
*/3  *  *  *  *  python emc_uemcli_script.py --device_ip {$ip} --device_user {$user} --device_password {$pass} --zabbix_host_name {$zabbix host name}  --state

crontab -l 查看现有的定时任务