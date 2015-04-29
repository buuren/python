#!/usr/bin/python
# 1) generate kerberos ticket: kinit <username>
# 2) verify ticket: klist
# 3) cntlm -v -I -M https://www.google.com
# -*- coding: utf-8 -*-

import time
import re
import sys, requests
from requests_kerberos import HTTPKerberosAuth, OPTIONAL
from BeautifulSoup import BeautifulSoup
import datetime
import codecs
import os.path


d = datetime.datetime.now()
current_date = d.strftime("%Y-%m-%d")

fname = '/var/www/logs/contrib_log.html'

if os.path.isfile(fname):
	os.remove(fname)

file = open(fname, "ab")
file.write("<!DOCTYPE html>\n")
file.write("<html>\n")
file.write("<body>\n")

log_output = []

#Use CNTLM to setup NTLM proxy authentication.
proxies = {
	"https": "http://localhost:3128"
}

kerberos_auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)

def kerb_auth(url):

	global parse_output
	try:
		r = requests.get (
			url,
			auth=kerberos_auth,
			proxies=proxies,
			verify=False
		)
	except Exception:
		print 'Wrong URL or proxy settings'
		sys.exit(1)

	parse_output = r.content
	return parse_output

def convert_to_text(if_value):

	for each_value in if_value:
		text = ''.join(each_value.findAll(text=True))
		each_value_name = text.strip()
		return each_value_name

def parse_provider():

	url='http://URL_GOES.HERE'
	kerb_auth(url)

	for line in parse_output.splitlines(True):
		if "Something" in line:
			break
		else:
			parse_soup = BeautifulSoup(line)
			providers = parse_soup.findAll('div', attrs={'class': 'xuiDisplayText_Sm_Bold'})

			if providers:
				print "--------------------------------------------------------"
				for provider in providers:
					print convert_to_text(providers)

					#Search provider status in the same line
					parse_status = BeautifulSoup(line)
					statuses = parse_status.findAll('span', attrs={'class': 'tableEntry'})
					if statuses:
						print convert_to_text(statuses)
					else:
						statuses = parse_status.findAll('span', attrs={'class': 'strongHighlight'})
						if statuses:
							print convert_to_text(statuses)
						else:
							print "Could not find any status for %s" % provider_name

	print "--------------------------------------------------------"

def parse_content_logs():

	url = 'http://URL_GOES.HERE'
	kerb_auth(url)


	for line in parse_output.splitlines(True):
		log_url = BeautifulSoup(line)
		my_regex = r"" + re.escape(current_date)

		if re.search(my_regex, line, re.IGNORECASE):
			for ahref in log_url.findAll('a', href=True):
				log_link = ahref['href']
				print "Found log", log_link

				log_url = 'http://URL_GOES.HERE' + log_link
				kerb_auth(log_url)

				for line in parse_output.splitlines(True):
					ldap_soup = BeautifulSoup(line)
				
					for error_loop in ldap_soup.findAll('tr'):
						error_type = error_loop.contents[0].text
						error_date = error_loop.contents[1].text
						error_data = error_loop.contents[2].text
						
						if "Retrieved index design with search field" in error_data:
							pass
						else:
							s = u'%s | %s | %s' % (error_type, error_date, error_data)
							encoded_text = s.encode('ascii', 'ignore')
							file.write("\n<p>" + encoded_text + "</p>")
				return

	file.write("</body>\n")
	file.write("</html>\n")
	file.close()
