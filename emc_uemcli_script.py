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

def discover_device(discover_key,device_name,command,zabbix_host_name):
    ret_data = []
    timestampnow = int(time.time())
    uemcli_logger.debug("start to discover: "+discover_key)
    list_dev_name = os.popen(command).read().splitlines()
    uemcli_logger.debug("list_dev_name: ")
    uemcli_logger.debug(list_dev_name)
    tmp_list = []
    for dev_name in list_dev_name:
        tmp_dict = {}
        tmp_dict[device_name]=dev_name
        tmp_list.append(tmp_dict)
    ret_data.append("%s %s %s %s" % (zabbix_host_name, discover_key, timestampnow,convert_to_zabbix_json(tmp_list)))
    return ret_data


def discover(uemcli_user, uemcli_password, uemcli_ip, zabbix_host_name, list_discover_key):
    send2server_data = []
    cmd = "{0} -d {1} -u {2} -p {3}".format(uemcli_command,uemcli_ip,uemcli_user,uemcli_password)

    for discover_key in list_discover_key:
        uemcli_logger.debug("start to discover: ")
        if discover_key=='disk':
            command = cmd+" /env/disk show|grep '   ID'|awk '{print$4}'"
            device_name = "{#DISKNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='sp':
            command = cmd+" /env/sp show -detail|grep '   ID'|awk '{print$4}'"
            device_name = "{#SPNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='battery':
            command = cmd+" /env/bat show|grep '   ID'|awk '{print$4}'"
            device_name = "{#BATTERYNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='power_supply':
            command = cmd+" /env/ps show|grep '   ID'|awk '{print$4}'"
            device_name = "{#PSNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='lcc':
            command = cmd+" /env/lcc show|grep '   ID'|awk '{print$4}'"
            device_name = "{#LCCNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='ssd':
            command = cmd+" /env/ssd show|grep '   ID'|awk '{print$4}'"
            device_name = "{#SSDNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='dae':
            command = cmd+" /env/dae show|grep '   ID'|awk '{print$4}'"
            device_name = "{#DAENAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='dpe':
            command = cmd+" /env/dpe show|grep '   ID'|awk '{print$4}'"
            device_name = "{#DPENAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='mm':
            command = cmd+" /env/mm show|grep '   ID'|awk '{print$4}'"
            device_name = "{#MMNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='ssc':
            command = cmd+" /env/ssc show|grep '   ID'|awk '{print$4}'"
            device_name = "{#SSCNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='fan':
            command = cmd+" /env/fan show|grep '   ID'|awk '{print$4}'"
            device_name = "{#FANNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='iomodule':
            command = cmd+" /env/iomodule show|grep '   ID'|awk '{print$4}'"
            device_name = "{#IOMODULENAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='pool':
            command = cmd+" /stor/config/pool show -detail|grep '   ID'|awk '{print$4}'"
            device_name = "{#POOLNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='pool':
            command = cmd+" /stor/prov/luns/lun show -detail|grep '   ID'|awk '{print$4}'"
            device_name = "{#LUNNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='nas':
            command = cmd+" /net/nas/server show -detail|grep '   ID'|awk '{print$4}'"
            device_name = "{#NASNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='iscsi':
            command = cmd+" /net/iscsi/node show |grep '   ID'|awk '{print$4}'"
            device_name = "{#ISCSINAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='eth_port':
            command = cmd+" /net/port/eth show -detail|grep '   ID'|awk '{print$4}'"
            device_name = "{#ETHPORTNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='sas_port':
            command = cmd+" /net/port/sas show |grep '   ID'|awk '{print$4}'"
            device_name = "{#SASPORTNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='fc_port':
            command = cmd+" /net/port/fc show |grep '   ID'|awk '{print$4}'"
            device_name = "{#FCPORTNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
        elif discover_key=='fc_port':
            command = cmd+" /net/port/unc show -detail|grep '   ID'|awk '{print$4}'"
            device_name = "{#UNCPORTNAME}"
            send2server_data.extend(discover_device(discover_key,device_name,command,zabbix_host_name))
            
    return send_data_to_zabbix(send2server_data, zabbix_host_name)
            


def get_state(uemcli_user, uemcli_password, uemcli_ip, zabbix_host_name, list_discover_key):
    send2server_data = []
    cmd = "{0} -d {1} -u {2} -p {3}".format(uemcli_command,uemcli_ip,uemcli_user,uemcli_password)

    for discover_key in list_discover_key:
        timestampnow = int(time.time())
        uemcli_logger.debug("start to discover: ")
        if discover_key=='disk':
            uemcli_logger.debug("start to get state: "+discover_key)
            list_dev_name = os.popen( cmd+" /env/disk show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /env/disk show |grep 'Health state'|awk '{print$5}'").read().splitlines()
            list_capacity = os.popen( cmd+" /env/disk show -detail|grep 'Capacity'|awk '{print$3}'").read().splitlines()
            list_user_capacity = os.popen( cmd+" /env/disk show|grep 'User capacity'|awk '{print$4}'").read().splitlines()
            list_current_speed = os.popen( cmd+" /env/disk show -detail|grep 'Current speed'|awk '{print$4}'").read().splitlines()
            list_max_speed = os.popen( cmd+" /env/disk show -detail|grep 'Maximum speed'|awk '{print$4}'").read().splitlines()
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
            list_dev_name = os.popen( cmd+" /env/sp show -detail|grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /env/sp show -detail|grep 'Health state'|awk '{print$5}'").read().splitlines()
            list_memory_size = os.popen( cmd+" /env/sp show -detail|grep 'Memory size'|awk '{print$4}'").read().splitlines()
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "sp.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "sp.memory_size[{}]".format(dev_name), timestampnow,list_memory_size[count])) if (len(list_memory_size)>count) and (list_memory_size[count]!='')  else uemcli_logger.debug("list_memory_size[count] is null")
                count+=1
        elif discover_key=='battery':
            uemcli_logger.debug("start to get state: "+discover_key)
            list_dev_name = os.popen( cmd+" /env/bat show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /env/bat show |grep 'Health state'|awk '{print$5}'").read().splitlines()
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "battery.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='power_supply':
            uemcli_logger.debug("start to get state: "+discover_key)
            list_dev_name = os.popen( cmd+" /env/ps show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /env/ps show |grep 'Health state'|awk '{print$5}'").read().splitlines()
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "power_supply.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='lcc':
            uemcli_logger.debug("start to get state: "+discover_key)
            list_dev_name = os.popen( cmd+" /env/lcc show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /env/lcc show |grep 'Health state'|awk '{print$5}'").read().splitlines()
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "lcc.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='ssd':
            uemcli_logger.debug("start to get state: "+discover_key)
            list_dev_name = os.popen( cmd+" /env/ssd show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /env/ssd show |grep 'Health state'|awk '{print$5}'").read().splitlines()
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "ssd.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='dae':
            uemcli_logger.debug("start to get state: "+discover_key)
            list_dev_name = os.popen( cmd+" /env/dae show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /env/dae show |grep 'Health state'|awk '{print$5}'").read().splitlines()
            list_power = os.popen( cmd+" /env/dae show |grep 'Power (Present)'|awk '{print$4}'").read().splitlines()            
            list_temperature = os.popen( cmd+" /env/dae show -detail|grep 'Temperature (Present)'|awk '{print$6}'").read().splitlines()   
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
            list_dev_name = os.popen( cmd+" /env/dpe show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /env/dpe show |grep 'Health state'|awk '{print$5}'").read().splitlines()
            list_power = os.popen( cmd+" /env/dpe show -detail|grep 'Power (Present)'|awk '{print$4}'").read().splitlines()           
            list_temperature = os.popen( cmd+" /env/dpe show -detail|grep 'Temperature (Present)'|awk '{print$6}'").read().splitlines()   
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
            list_dev_name = os.popen( cmd+" /env/mm show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /env/mm show |grep 'Health state'|awk '{print$5}'").read().splitlines()
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "mm.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='ssc':
            uemcli_logger.debug("start to get state: "+discover_key)
            list_dev_name = os.popen( cmd+" /env/ssc show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /env/ssc show |grep 'Health state'|awk '{print$5}'").read().splitlines()
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "ssc.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='fan':
            uemcli_logger.debug("start to get state: "+discover_key)
            list_dev_name = os.popen( cmd+" /env/fan show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /env/fan show |grep 'Health state'|awk '{print$5}'").read().splitlines()
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "fan.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='iomodule':
            uemcli_logger.debug("start to get state: "+discover_key)
            list_dev_name = os.popen( cmd+" /env/iomodule show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /env/iomodule show |grep 'Health state'|awk '{print$5}'").read().splitlines()
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "iomodule.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='pool':
            uemcli_logger.debug("start to get state: "+discover_key)
            list_dev_name = os.popen( cmd+" /stor/config/pool show -detail |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /stor/config/pool show -detail |grep 'Health state'|awk '{print$5}'").read().splitlines()
            list_total_space = os.popen( cmd+" /stor/config/pool show -detail |grep 'Total space'|awk '{print$4}'").read().splitlines()
            list_current_allocation = os.popen( cmd+" /stor/config/pool show -detail |grep 'Current allocation'|awk '{print$4}'").read().splitlines()
            list_preallocated_space = os.popen( cmd+" /stor/config/pool show -detail |grep 'Preallocated space'|awk '{print$4}'").read().splitlines()
            list_remaining_space = os.popen( cmd+" /stor/config/pool show -detail |grep 'Remaining space'|awk '{print$4}'").read().splitlines()
            list_subscription = os.popen( cmd+" /stor/config/pool show -detail |grep 'Subscription  '|awk '{print$3}'").read().splitlines()
            list_subscription_percent = os.popen( cmd+" /stor/config/pool show -detail |grep 'Subscription percent'|awk '{print$4}'").read().splitlines()
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
            list_dev_name = os.popen( cmd+"/stor/prov/luns/lun show -detail|grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+"/stor/prov/luns/lun show -detail|grep 'Health state'|awk '{print$5}'").read().splitlines()
            list_size = os.popen( cmd+"/stor/prov/luns/lun show -detail|grep 'Size'|awk '{print$3}'").read().splitlines()
            list_current_allocation = os.popen( cmd+"/stor/prov/luns/lun show -detail|grep 'Current allocation'|awk '{print$4}'").read().splitlines()
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
            list_dev_name = os.popen( cmd+" /net/nas/server show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /net/nas/server show |grep 'Health state'|awk '{print$5}'").read().splitlines()
            list_fs_used = os.popen( cmd+" /net/nas/server show |grep 'File space used'|awk '{print$5}'").read().splitlines()
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
            list_dev_name = os.popen( cmd+" /net/iscsi/node show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /net/iscsi/node show|grep 'Health state'|awk '{print$5}'").read().splitlines()
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            count = 0
            for dev_name in list_dev_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "iscsi.health[{}]".format(dev_name), timestampnow,list_health_state[count].strip('(').strip(')'))) if (len(list_health_state)>count) and (list_health_state[count]!='')  else uemcli_logger.debug("list_health_state[count] is null")
                count+=1
        elif discover_key=='eth_port':
            uemcli_logger.debug("start to get state: "+discover_key)
            list_dev_name = os.popen( cmd+" /net/port/eth show -detail |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /net/port/eth show -detail |grep 'Health state'|awk '{print$5}'").read().splitlines()
            list_speed = os.popen( cmd+" /net/port/eth show -detail |grep '  Speed  '|awk '{print$3}'").read().splitlines()
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
            list_dev_name = os.popen( cmd+" /net/port/sas show |grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /net/port/sas show |grep 'Health state'|awk '{print$5}'").read().splitlines()
            list_speed = os.popen( cmd+" /net/port/sas show |grep '  Speed  '|awk '{print$3}'").read().splitlines()
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
            list_dev_name = os.popen( cmd+" /net/port/fc show|grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /net/port/fc show|grep 'Health state'|awk '{print$5}'").read().splitlines()
            list_speed = os.popen( cmd+" /net/port/fc show|grep 'Speed'|awk '{print$3}'").read().splitlines()
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
            list_dev_name = os.popen( cmd+" /net/port/unc show -detial|grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /net/port/unc show -detial|grep 'Health state'|awk '{print$5}'").read().splitlines()
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

