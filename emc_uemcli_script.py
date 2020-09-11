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
uemcli_logger.setLevel(logging.DEBUG)

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



def discover(uemcli_user, uemcli_password, uemcli_ip, zabbix_host_name, list_discover_key):
    send2server_data = []
    cmd = "{0} -d {1} -u {2} -p {3}".format(uemcli_command,uemcli_ip,uemcli_user,uemcli_password)

    for discover_key in list_discover_key:
        timestampnow = int(time.time())
        uemcli_logger.debug("start to discover: ")
        if discover_key=='disk':
            uemcli_logger.debug("start to discover: "+discover_key)
            list_disk_name = os.popen( cmd+" /env/disk show|grep '   ID'|awk '{print$4}'").read().splitlines()
            uemcli_logger.debug("list_disk_name: ")
            uemcli_logger.debug(list_disk_name)
            tmp_list = []
            for disk_name in list_disk_name:
                tmp_dict = {}
                tmp_dict["{#DISKNAME}"]=disk_name
                tmp_list.append(tmp_dict)
            send2server_data.append("%s %s %s %s" % (zabbix_host_name, discover_key, timestampnow,convert_to_zabbix_json(tmp_list)))

    return send_data_to_zabbix(send2server_data, zabbix_host_name)
            


def get_state(uemcli_user, uemcli_password, uemcli_ip, zabbix_host_name, list_discover_key):
    send2server_data = []
    cmd = "{0} -d {1} -u {2} -p {3}".format(uemcli_command,uemcli_ip,uemcli_user,uemcli_password)

    for discover_key in list_discover_key:
        timestampnow = int(time.time())
        uemcli_logger.debug("start to discover: ")
        if discover_key=='disk':
            uemcli_logger.debug("start to statu: "+discover_key)
            list_disk_name = os.popen( cmd+" /env/disk show|grep '   ID'|awk '{print$4}'").read().splitlines()
            list_health_state = os.popen( cmd+" /env/disk show|grep 'Health state'|awk '{print$5}'").read().splitlines()
            list_user_capacity = os.popen( cmd+" /env/disk show|grep 'User capacity'|awk '{print$4}'").read().splitlines()
            uemcli_logger.debug("list_health_state: ")
            uemcli_logger.debug(list_health_state)
            uemcli_logger.debug("list_user_capacity: ")
            uemcli_logger.debug(list_user_capacity)
            count = 0
            for disk_name in list_disk_name:
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "disk.health[{}]".format(disk_name), timestampnow,list_health_state[count].strip('(').strip(')')))
                send2server_data.append("%s %s %s %s" % (zabbix_host_name, "disk.user_capacity[{}]".format(disk_name), timestampnow,list_user_capacity[count]))
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

	list_discover_key = ['disk']
    #,'ssd','ethernetPort','fcPort','sasPort','fan','powerSupply','storageProcessor','lun','pool','dae','dpe','ioModule','lcc','memoryModule','ssc','uncommittedPort','disk']
	if arguments.discovery:
		result_discovery = discover(arguments.device_user, arguments.device_password, arguments.device_ip,  arguments.zabbix_host_name, list_discover_key)
		print (result_discovery)
	elif arguments.state:
		result_status = get_state(arguments.device_user, arguments.device_password, arguments.device_ip,  arguments.zabbix_host_name, list_discover_key)
		print (result_status)

if __name__ == "__main__":
	main()

