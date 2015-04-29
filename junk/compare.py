#!/usr/bin/python
import MySQLdb

# connect
db = MySQLdb.connect(host="", user="", passwd="",db="")

cursor = db.cursor()

# execute SQL select statement
cursor.execute("SELECT * FROM stats")

# get the number of rows in the resultset
numrows = int(cursor.rowcount)

from Tkinter import *

root = Tk()

w = Label(root, text="Hello, world!")
w.pack()

root.mainloop()
# get and display one row at a time
print '----------------|---------------------------|----------------------|----------------------|-----------------|--------|---------------------------------------------------------------------------------------------------------------------'
print '    PC NAME     |        USER NAME          |     IP ADDRESS       |     MAC ADDRESS      |    WORKGROUP    | UPTIME |'
print '----------------|---------------------------|----------------------|----------------------|-----------------|--------|---------------------------------------------------------------------------------------------------------------------'
for x in range(0,numrows):
	row = cursor.fetchone()
	pc_name = row[1]
	user_names = row[2]
	ip_address = row[3]
	mac_address = row[4]
	#mac_address = mac_address[0]
	workgroup = row[5]
	uptime_hours = row[6]
	cpu = row[7]
	mother = row[8]
	ram = row[9]
	os_name = row[10]
	os_date = row[11]
	os_key = row[12]
	os_sp = row[14]
	office_ver = row[16]
	office_key = row[17]
	aida = row[18]
	firewall = row[19]
	asukoht = row[20]
	arve_nr = row[21]
	tarnija = row[22]
	serial_number = row[23]
	paigaldus = row[24]
	monitor_name = row[25]
	monitor_manu = row[26]
	monitor_seri = row[27]
	monitor_code = row[28]
	monitor_week = row[29]
	monitor_year = row[30]
	
	print '{0:15s} | {1:25s} | {2:20s} | {3:20s} | {4:15s} | {5:6s} | {6:40s} | {7:30s} | {8:10s} | {9:35s} '.format(pc_name, 
	user_names, ip_address, mac_address, workgroup, uptime_hours, cpu, mother, ram, os_name, os_date, os_key, os_sp, office_ver, office_key, 
	aida, firewall, asukoht,arve_nr, tarnija, serial_number, paigaldus, monitor_name, monitor_manu, monitor_seri, monitor_code, monitor_week, monitor_year)

#for x in range(1,11):
#	print '{0:2d} {1:3d} {2:4d}'.format(x, x, x)
