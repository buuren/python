import random
import os
import socket
import time
import re

'''
http://courses.cs.ttu.ee/pages/Malware:ITX8042:2014:LAB2
'''

class MyNumber():
    def __init__(self, my_date, mod, add = 0):
        self.my_date = my_date
        self.mod = mod
        self.add = add

    def GetNumber(self):
        sum_my_date = sum([int(char) for char in str(self.my_date)])
        return (sum_my_date + random.randint(0, 32767)) % self.mod + self.add


def find_value(my_number, filename):
    counter = 0
    file_content = open(filename, 'r')
    for line in file_content:
        if counter == my_number:
            return str(line.replace(' ', '')).rstrip()
        counter += 1


my_number_1 = MyNumber(40, 106).GetNumber()
my_number_2 = MyNumber(40, 2000, 400).GetNumber()
my_number_4 = MyNumber(40, 3228).GetNumber()

print 'My number for exercise 1 is:', my_number_1
print 'My number for exercise 2 is:', my_number_2
print 'My number for exercise 4 is:', my_number_4
print ''
names = '%s/names.txt' % os.getcwd()
ips = '%s/ips.txt' % os.getcwd()

"""
Exercise 1
"""
if find_value(my_number_1, names):
    print 'Doing exercise 1...'
    line =  find_value(my_number_1, names)
    try:
        print 'Getting IP address of:', line
        ip_addr = socket.gethostbyname(line)
        print 'Found IP adress:', ip_addr
        print 'TODO: Searching for more hosts...'
    except socket.gaierror:
        print 'Unable to find ip addres of:', line
    except Exception:
        print 'General error:', line
else:
    print 'Could not find entry %s in filename %s' % (my_number_1, names)
print ''
"""
Exercise 2
"""
if find_value(my_number_2, ips):
    print 'Doing exercise 2'
    ip_pattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    search_ip = re.search(ip_pattern, find_value(my_number_2, ips))
    if search_ip:
        ip_addr = search_ip.group()
        print 'Found IP address:', ip_addr
        print 'TODO: Find owner (dig -x)'
    else:
        print 'Returned entry does not match IP address:', find_value(my_number_2, ips)
else:
    print 'Could not find entry %s in filename %s' % (my_number_2, ips)
print ''
"""
Exercise 3
"""
print ''
"""
Exercise 4
"""
