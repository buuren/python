import re
import os
from datetime import datetime

#example of logs https://github.com/buuren/python/edit/master/done/log_example.txt

startTime = datetime.now()

d = {}
m = []

dirname = '/home/user/logs'

for filename in os.listdir(dirname):

    full_filename = dirname + '/' + filename
    f = open(full_filename, 'r')

    # find 00:06:21 in [06/Apr/2014:00:06:21 +0200]
    time_compile = re.compile(r'\[.*?:(\d+):.*?\]')

    # find www.google.com in "https://www.google.com/"
    url_compile = re.compile(r'www.\w+.\w+')

    # find 83.215.5.41 in 83.215.5.41 - - [06/Apr/2014:00:07:07 +0200] "GET
    ip_compile = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}[^0-9]')

    for line in f:
        if 'HTTP/1.1" 200' in line:
            time_z = re.search(time_compile, line).group(1)
            if time_z >= '20' or time_z <= '01':
                url_ = re.search(url_compile, line)

                if url_:
                    url = url_.group()
                    if 'something' in url:
                        ip = re.search(ip_compile, line).group()

                        if url in d:
                            new_ip = True
                            ix = -1
                            for each_ip in d[url]:
                                ix += 1
                                if ip in each_ip:
                                    d[url][ix][1] += 1
                                    new_ip = False
                                    break

                            if new_ip is True:
                                ip_list = [ip, 1]
                                d[url].append(ip_list)
                        else:
                            ip_list = [ip, 1]
                            d[url] = [ip_list]

    print 'File done: %s' % full_filename
    print(datetime.now()-startTime)

sorts = d.items()
h1 = []

for k, v in sorts:
    h1.append(len(v))
    print '%s\t%s' % (k, len(v))
    m.append(len(v))

print ""
print 'Total requests: %s' % (sum(h1))
print(datetime.now()-startTime)
