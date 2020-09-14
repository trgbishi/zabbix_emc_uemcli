#!/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import argparse
import sys
import json
import subprocess
import logging
import logging.handlers
import requests
import urllib3


# Create log-object
LOG_FILENAME = "/tmp/emc_uemcli_script.log"
uemcli_command = "/opt/emc/uemcli/bin/uemcli.sh"
uemcli_logger = logging.getLogger("uemcli_logger")
uemcli_logger.setLevel(logging.CRITICAL)

# Set handler
uemcli_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1024*1024, backupCount=5)
uemcli_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set formatter for handler
uemcli_handler.setFormatter(uemcli_formatter)

# Add handler to log-object
uemcli_logger.addHandler(uemcli_handler)


def convert_to_zabbix_json(data):
        output = json.dumps({"data": data}, indent = None, separators = (',',': '))
        return output


def send_data_to_zabbix(zabbix_data, storage_name):
        sender_command = "/usr/bin/zabbix_sender"
        config_path = "/etc/zabbix/zabbix_agentd.conf"
        time_of_create_file = int(time.time())
        temp_file = "/tmp/{0}_{1}.tmp".format(storage_name, time_of_create_file)

        with open(temp_file, "w") as f:
                f.write("")
                f.write("\n".join(zabbix_data))
        
        uemcli_logger.debug("zabbix_data: ")
        uemcli_logger.debug(zabbix_data)
        send_code = subprocess.call([sender_command, "-vv", "-c", config_path, "-s", storage_name, "-T", "-i", temp_file], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        os.remove(temp_file)
        return send_code

def discover_device(discover_key,device_name,command,zabbix_host_name,grep_key,awk_num):
    ret_data = []
    timestampnow = int(time.time())
    uemcli_logger.debug("start to discover: "+discover_key)
    lines = os.popen(command).read().splitlines()

    list_dev_name = as_linux_awk(as_linux_grep(lines,grep_key),awk_num)
    uemcli_logger.debug("list_dev_name: ")
    uemcli_logger.debug(list_dev_name)
    tmp_list = []
    for dev_name in list_dev_name:
        tmp_dict = {}
        tmp_dict[device_name]=dev_name
        tmp_list.append(tmp_dict)
    ret_data.append("%s %s %s %s" % (zabbix_host_name, discover_key, timestampnow,convert_to_zabbix_json(tmp_list)))
    return ret_data

def as_linux_grep(lines,grep_key):
    grep_line = []
    for line in lines:
        if grep_key in line:
            grep_line.append(line)
    uemcli_logger.debug("grep_line: ")
    uemcli_logger.debug(grep_line)
    uemcli_logger.debug("grep_key: ")
    uemcli_logger.debug(grep_key)
    return grep_line

def as_linux_awk(lines,awk_num):
    awk_num-=1
    ret_list = []
    uemcli_logger.debug("lines: ")
    uemcli_logger.debug(lines)
    uemcli_logger.debug("awk_num: ")
    uemcli_logger.debug(awk_num)
    for line in lines:
        tmp_list = line.split()
        ret_list.append(tmp_list[awk_num]) if len(tmp_list)>awk_num else ret_list.append('')
    uemcli_logger.debug("ret_list: ")
    uemcli_logger.debug(ret_list)

    return ret_list


def discover(uemcli_user, uemcli_password, uemcli_ip, zabbix_host_name, list_discover_key):
    send2server_data = []
    cmd = "{0} -d {1} -u {2} -p {3}".format(uemcli_command,uemcli_ip,uemcli_user,uemcli_password)

    for discover_key in list_discover_key:
        uemcli_logger.debug("start to discover: ")
        if discover_key=='disk':
            command = cmd+" /env/disk show"
            device_name = "{#DISKNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='sp':
            command = cmd+" /env/sp show -detail"
            device_name = "{#SPNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='battery':
            command = cmd+" /env/bat show"
            device_name = "{#BATTERYNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='power_supply':
            command = cmd+" /env/ps show"
            device_name = "{#PSNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='lcc':
            command = cmd+" /env/lcc show"
            device_name = "{#LCCNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='ssd':
            command = cmd+" /env/ssd show"
            device_name = "{#SSDNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='dae':
            command = cmd+" /env/dae show"
            device_name = "{#DAENAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='dpe':
            command = cmd+" /env/dpe show"
            device_name = "{#DPENAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='mm':
            command = cmd+" /env/mm show"
            device_name = "{#MMNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='ssc':
            command = cmd+" /env/ssc show"
            device_name = "{#SSCNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='fan':
            command = cmd+" /env/fan show"
            device_name = "{#FANNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='iomodule':
            command = cmd+" /env/iomodule show"
            device_name = "{#IOMODULENAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='pool':
            command = cmd+" /stor/config/pool show -detail"
            device_name = "{#POOLNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='pool':
            command = cmd+" /stor/prov/luns/lun show -detail"
            device_name = "{#LUNNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='nas':
            command = cmd+" /net/nas/server show -detail"
            device_name = "{#NASNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='iscsi':
            command = cmd+" /net/iscsi/node show "
            device_name = "{#ISCSINAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='eth_port':
            command = cmd+" /net/port/eth show -detail"
            device_name = "{#ETHPORTNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='sas_port':
            command = cmd+" /net/port/sas show "
            device_name = "{#SASPORTNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='fc_port':
            command = cmd+" /net/port/fc show "
            device_name = "{#FCPORTNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
        elif discover_key=='fc_port':
            command = cmd+" /net/port/unc show -detail"
            device_name = "{#UNCPORTNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name,'   ID',4))
            
    return send_data_to_zabbix(send2server_data, zabbix_host_name)
            


def get_state(uemcli_user, uemcli_password, uemcli_ip, zabbix_host_name, list_discover_key):
    send2server_data = []
    cmd = "{0} -d {1} -u {2} -p {3}".format(uemcli_command,uemcli_ip,uemcli_user,uemcli_password)

    for discover_key in list_discover_key:
        timestampnow = int(time.time())
        uemcli_logger.debug("start to discover: ")
        if discover_key=='disk':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /env/disk show").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            list_capacity = as_linux_awk(as_linux_grep(lines,'Capacity'),3)
            list_user_capacity = as_linux_awk(as_linux_grep(lines,'User capacity'),4)
            list_current_speed = as_linux_awk(as_linux_grep(lines,'Current speed'),4)
            list_max_speed = as_linux_awk(as_linux_grep(lines,'Maximum speed'),4)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            uemcli_logger.debug("list_capacity: ")
            uemcli_logger.debug(list_capacity)
            uemcli_logger.debug("list_user_capacity: ")
            uemcli_logger.debug(list_user_capacity)
            uemcli_logger.debug("list_current_speed: ")
            uemcli_logger.debug(list_current_speed)
            uemcli_logger.debug("list_max_speed: ")
            uemcli_logger.debug(list_max_speed)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "disk.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "disk.capacity[{}]".format(dev_name), timestampnow,list_capacity[count])) if (len(list_capacity)>count) and (list_capacity[count]!='')  else uemcli_logger.debug("list_capacity[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "disk.user_capacity[{}]".format(dev_name), timestampnow,list_user_capacity[count])) if (len(list_user_capacity)>count) and (list_user_capacity[count]!='')  else uemcli_logger.debug("list_user_capacity[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "disk.current_speed[{}]".format(dev_name), timestampnow,list_current_speed[count])) if (len(list_current_speed)>count) and (list_current_speed[count]!='')  else uemcli_logger.debug("list_current_speed[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "disk.max_speed[{}]".format(dev_name), timestampnow,list_max_speed[count])) if (len(list_max_speed)>count) and (list_max_speed[count]!='')  else uemcli_logger.debug("list_max_speed[count] is null")
                count+=1
        elif discover_key=='sp':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /env/sp show -detail").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            list_memory_size = as_linux_awk(as_linux_grep(lines,'Memory size'),4)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "sp.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "sp.memory_size[{}]".format(dev_name), timestampnow,list_memory_size[count])) if (len(list_memory_size)>count) and (list_memory_size[count]!='')  else uemcli_logger.debug("list_memory_size[count] is null")
                count+=1
        elif discover_key=='battery':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /env/bat show ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "battery.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='power_supply':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /env/ps show ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "power_supply.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='lcc':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /env/lcc show ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "lcc.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='ssd':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /env/ssd show ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "ssd.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='dae':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /env/dae show ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            list_power = as_linux_awk(as_linux_grep(lines,'Power (Present)'),4)
            list_temperature = as_linux_awk(as_linux_grep(lines,'Temperature (Present)'),6)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "dae.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "dae.power[{}]".format(dev_name), timestampnow,list_power[count].strip('(').strip('°'))) if (len(list_power)>count) and (list_power[count]!='')  else uemcli_logger.debug("list_power[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "dae.temperature[{}]".format(dev_name), timestampnow,list_temperature[count].strip('(').strip('°'))) if (len(list_temperature)>count) and (list_temperature[count]!='')  else uemcli_logger.debug("list_temperature[count] is null")
                count+=1
        elif discover_key=='dpe':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /env/dpe show ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            list_power = as_linux_awk(as_linux_grep(lines,'Power (Present)'),4)
            list_temperature = as_linux_awk(as_linux_grep(lines,'Temperature (Present)'),6)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)   
            uemcli_logger.debug("list_power: ")
            uemcli_logger.debug(list_power)   
            uemcli_logger.debug("list_temperature: ")
            uemcli_logger.debug(list_temperature)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "dpe.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "dpe.power[{}]".format(dev_name), timestampnow,list_power[count].strip('(').strip('°'))) if (len(list_power)>count) and (list_power[count]!='')  else uemcli_logger.debug("list_power[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "dpe.temperature[{}]".format(dev_name), timestampnow,list_temperature[count].strip('(').strip('°'))) if (len(list_temperature)>count) and (list_temperature[count]!='')  else uemcli_logger.debug("list_temperature[count] is null")
                count+=1
        elif discover_key=='mm':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /env/mm show ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "mm.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='ssc':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /env/ssc show ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "ssc.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='fan':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /env/fan show ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "fan.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='iomodule':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /env/iomodule show ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "iomodule.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='pool':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /stor/config/pool show -detail ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            list_total_space = as_linux_awk(as_linux_grep(lines,'Total space'),4)
            list_current_allocation = as_linux_awk(as_linux_grep(lines,'Current allocation'),4)
            list_preallocated_space = as_linux_awk(as_linux_grep(lines,'Preallocated space'),4)
            list_remaining_space = as_linux_awk(as_linux_grep(lines,'Remaining space'),4)
            list_subscription = as_linux_awk(as_linux_grep(lines,'Subscription  '),3)
            list_subscription_percent = as_linux_awk(as_linux_grep(lines,'Subscription percent'),4)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            uemcli_logger.debug("list_total_space: ")
            uemcli_logger.debug(list_total_space)
            uemcli_logger.debug("list_current_allocation: ")
            uemcli_logger.debug(list_current_allocation)
            uemcli_logger.debug("list_preallocated_space: ")
            uemcli_logger.debug(list_preallocated_space)
            uemcli_logger.debug("list_remaining_space: ")
            uemcli_logger.debug(list_remaining_space)
            uemcli_logger.debug("list_subscription: ")
            uemcli_logger.debug(list_subscription)
            uemcli_logger.debug("list_subscription_percent: ")
            uemcli_logger.debug(list_subscription_percent)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "pool.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "pool.total_space[{}]".format(dev_name), timestampnow,list_total_space[count])) if (len(list_total_space)>count) and (list_total_space[count]!='')  else uemcli_logger.debug("list_total_space[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "pool.current_allocation[{}]".format(dev_name), timestampnow,list_current_allocation[count])) if (len(list_current_allocation)>count) and (list_current_allocation[count]!='')  else uemcli_logger.debug("list_current_allocation[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "pool.preallocated_space[{}]".format(dev_name), timestampnow,list_preallocated_space[count])) if (len(list_preallocated_space)>count) and (list_preallocated_space[count]!='')  else uemcli_logger.debug("list_preallocated_space[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "pool.remaining_space[{}]".format(dev_name), timestampnow,list_remaining_space[count])) if (len(list_remaining_space)>count) and (list_remaining_space[count]!='')  else uemcli_logger.debug("list_remaining_space[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "pool.subscription[{}]".format(dev_name), timestampnow,list_subscription[count])) if (len(list_subscription)>count) and (list_subscription[count]!='')  else uemcli_logger.debug("list_subscription[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "pool.subscription_percent[{}]".format(dev_name), timestampnow,list_subscription_percent[count].strip('%'))) if (len(list_subscription_percent)>count) and (list_subscription_percent[count]!='')  else uemcli_logger.debug("list_subscription_percent[count] is null")
                count+=1
        elif discover_key=='lun':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+"/stor/prov/luns/lun show -detail").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            list_size = as_linux_awk(as_linux_grep(lines,'Size'),3)
            list_current_allocation = as_linux_awk(as_linux_grep(lines,'Current allocation'),4)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            uemcli_logger.debug("list_size: ")
            uemcli_logger.debug(list_size)
            uemcli_logger.debug("list_current_allocation: ")
            uemcli_logger.debug(list_current_allocation)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "lun.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "lun.size[{}]".format(dev_name), timestampnow,list_size[count])) if (len(list_size)>count) and (list_size[count]!='')  else uemcli_logger.debug("list_size[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "lun.current_allocation[{}]".format(dev_name), timestampnow,list_current_allocation[count])) if (len(list_current_allocation)>count) and (list_current_allocation[count]!='')  else uemcli_logger.debug("list_current_allocation[count] is null")
                count+=1
        elif discover_key=='nas':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /net/nas/server show ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            list_fs_used = as_linux_awk(as_linux_grep(lines,'File space used'),5)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            uemcli_logger.debug("list_fs_used: ")
            uemcli_logger.debug(list_fs_used)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "nas.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "nas.fs_used[{}]".format(dev_name), timestampnow,list_fs_used[count])) if (len(list_fs_used)>count) and (list_fs_used[count]!='')  else uemcli_logger.debug("list_fs_used[count] is null")
                count+=1
        elif discover_key=='iscsi':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /net/iscsi/node show ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "iscsi.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='eth_port':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /net/port/eth show -detail ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            list_speed = as_linux_awk(as_linux_grep(lines,'  Speed  '),3)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            uemcli_logger.debug("list_speed: ")
            uemcli_logger.debug(list_speed)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "eth_port.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "eth_port.speed[{}]".format(dev_name), timestampnow,list_speed[count])) if (len(list_speed)>count) and (list_speed[count]!='')  else uemcli_logger.debug("list_speed[count] is null")
                count+=1
        elif discover_key=='sas_port':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /net/port/sas show ").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            list_speed = as_linux_awk(as_linux_grep(lines,'  Speed  '),3)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            uemcli_logger.debug("list_speed: ")
            uemcli_logger.debug(list_speed)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "sas_port.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "sas_port.speed[{}]".format(dev_name), timestampnow,list_speed[count])) if (len(list_speed)>count) and (list_speed[count]!='')  else uemcli_logger.debug("list_speed[count] is null")
                count+=1
        elif discover_key=='fc_port':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /net/port/fc show").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            list_speed = as_linux_awk(as_linux_grep(lines,'Speed'),3)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            uemcli_logger.debug("list_speed: ")
            uemcli_logger.debug(list_speed)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "fc_port.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "fc_port.speed[{}]".format(dev_name), timestampnow,list_speed[count])) if (len(list_speed)>count) and (list_speed[count]!='')  else uemcli_logger.debug("list_speed[count] is null")
                count+=1
        elif discover_key=='unc_port':
            uemcli_logger.debug("start to get state: "+discover_key)
            lines = os.popen( cmd+" /net/port/unc show -detial").read().splitlines()
            list_dev_name = as_linux_awk(as_linux_grep(lines,'   ID'),4)
            list_health_state = as_linux_awk(as_linux_grep(lines,'Health state'),5)
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "unc_port.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
    return send_data_to_zabbix(send2server_data, zabbix_host_name)



def main():
	# Parsing arguments
	uemcli_parser = argparse.ArgumentParser()
	uemcli_parser.add_argument('--device_ip', action="store", help="Where to connect", required=True)
	uemcli_parser.add_argument('--device_user', action="store", required=True)
	uemcli_parser.add_argument('--device_password', action="store", required=True)
	uemcli_parser.add_argument('--zabbix_host_name', action="store", required=True)

	group = uemcli_parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--discovery', action ='store_true')
	group.add_argument('--state', action='store_true')
	arguments = uemcli_parser.parse_args()

	uemcli_logger.debug("arguments.device_ip: "+arguments.device_ip)
	uemcli_logger.debug("arguments.device_user: "+arguments.device_user)
	uemcli_logger.debug("arguments.device_password: "+arguments.device_password)
	uemcli_logger.debug("arguments.zabbix_host_name: "+arguments.zabbix_host_name)

	list_discover_key = ['disk','sp','battery','power_supply','lcc','ssd','dae','dpe','mm','ssc','fan','iomodule','pool','lun','nas','iscsi','eth_port','sas_port','fc_port','unc_port']
    #,'ssd','ethernetPort','fcPort','sasPort','fan','powerSupply','storageProcessor','lun','pool','dae','dpe','ioModule','lcc','memoryModule','ssc','uncommittedPort','disk']
	if arguments.discovery:
		result_discovery = discover(arguments.device_user, arguments.device_password, arguments.device_ip,  arguments.zabbix_host_name, list_discover_key)
		print (result_discovery)
	elif arguments.state:
		result_status = get_state(arguments.device_user, arguments.device_password, arguments.device_ip,  arguments.zabbix_host_name, list_discover_key)
		print (result_status)

if __name__ == "__main__":
	main()

