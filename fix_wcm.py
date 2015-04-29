# 	Python script to find your current IP address and replace IP address in files
# Will search IP address in format "172.xxx.xxx.xN" in ipconfig output and edit files 
# tnsnames.ora, listener.ora and hosts to place the new IP address. If at least 1 change
# has been made, the script will rename computer name and restart the machine.
# 
# 	Problem: in DHCP environment with IP lease time, unable to install oracle db 11g 
# on VirtualBox using localhost. The db requires a fully qualified domain name. 
#
# 	Fix: install oracle db using your current IP address and add python script to logon
# scripts, each time user logs in, the script is launched and modifies configuration files.
#
#	Modify file locations
#
#	Python: Python 2.7.5 (default, May 15 2013, 22:43:36) [MSC v.1500 32 bit (Intel)] on win32

import os
import socket
import re
import fileinput
import time 
import subprocess
import string
import random

#-------------------------- Declare some variables ---------------------------------
restart = []
tnsnames_file = r'E:\app\wcm\product\11.2.0\dbhome_1\NETWORK\ADMIN\tnsnames.ora'
listener_file = r'E:\app\wcm\product\11.2.0\dbhome_1\NETWORK\ADMIN\listener.ora'
hosts_file = 'C:\Windows\System32\drivers\etc\hosts'
#-------------------------- Current local IP address -------------------------------
def find_ip_addr():
	proc = subprocess.Popen('ipconfig', shell = True, stdout=subprocess.PIPE)
	rawtxt = proc.communicate()[0].upper().splitlines()
	for each_line in rawtxt:
		if 'IPV4' in each_line:
			proc =  re.search(r'172.\d{1,3}\.\d{1,3}\.\d{1,3}', each_line)
			if proc:
				local_ip_addr = proc.group()
				return local_ip_addr

local_ip_addr = find_ip_addr()

while local_ip_addr != "":
	local_ip_addr = find_ip_addr()
	if not local_ip_addr:
		print "IP not found. Searching again..."
		find_ip_addr()
		time.sleep(3)
	else:
		break
#------------------------------------------------------------------------------------
if not os.path.exists(tnsnames_file):
	print "config_file does not exist"
else:
	read_tnsnames_file = open(tnsnames_file, 'r').read()
	text_tnsnames_file = read_tnsnames_file.decode('utf-8')
	tnsnames_ip = re.findall("172.\d{1,3}.\d{1,3}.\d+", text_tnsnames_file)
	for each_ip_address in tnsnames_ip:
		if local_ip_addr == each_ip_address:
			print "TNSNAMES IP: OK"
			restart_tns = 0
			restart.append(restart_tns)
		else:
			print "changing IP..."
			for line in fileinput.input(tnsnames_file, inplace=True):
				print re.sub(each_ip_address,local_ip_addr,line),
			restart_tns = 1
			restart.append(restart_tns)
#-----------------------------------------------------------------------------------
if not os.path.exists(listener_file):
	print "config_file does not exist"
else:
	read_listener_file = open(listener_file, 'r').read()
	text_listener_file = read_listener_file.decode('utf-8')
	listener_ip = re.findall("172.\d{1,3}.\d{1,3}.\d+", text_listener_file)
	listener_ip = ''.join(listener_ip)
	if local_ip_addr == listener_ip:
		print "LISTENER IP: OK"
		restart_lis = 0
		restart.append(restart_lis)
	else:
		print "changing IP..."
		r = re.compile("172.\d{1,3}.\d{1,3}.\d+")
		for line in fileinput.input(listener_file, inplace=True):
			print re.sub(r,local_ip_addr,line),
		restart_lis = 1
		restart.append(restart_lis)
		
new_pc_name = "wcm_" + ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
old_pc_name = (socket.gethostname())

for each_restart in restart:
	if each_restart == 1:
		print "Renaming and restarting..."
		subprocess.call("wmic computersystem where caption='%s' call rename %s" % (old_pc_name, new_pc_name), shell=True)
		subprocess.call("shutdown -r -t 0", shell=True)
	
#----------------------------------------------------------------------------------------------------
with open(hosts_file, 'r') as file:
	data = file.readlines()

data[22] = '%s %s\n' % (local_ip_addr, old_pc_name)
data[23] = '%s localhost' % (local_ip_addr)

with open(hosts_file, 'w') as file:
	file.writelines( data )
