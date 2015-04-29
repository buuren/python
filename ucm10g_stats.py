# -*- coding: utf-8 -*-
"""
WCM statistic analyzer.
Requirements
1. Copy obj.conf from: .../config/obj.conf. Place to %USERHOME%/wcm
2. Copy entire folder of project files to to %USERHOME%/wcm
3.
"""
import requests
import os
import re
import kerberos_sspi as kerberos
from calendar import monthrange
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import calendar
import urllib2
import httplib
import urlparse
import multiprocessing
import datetime


startTime = datetime.datetime.now()
httplib.HTTPConnection.debuglevel = 0
internal = 0
external = 0
unknown = 0
now = datetime.datetime.now()
kerberos_location = "HTTP@your.sso.net"
http_user = 'user'
http_pass = 'pass'
user_profile = os.environ['USERPROFILE']
files_dir = user_profile + "/folder/"

find_weblayout = [
    os.path.join(root_dir, folder_name)
    for root_dir, sub_dirs, filename in os.walk(files_dir)
    for folder_name in sub_dirs
    if "weblayout" in folder_name
][0]

debug = False


class KerberosTicket:
    def __init__(self, service):
        __, krb_context = kerberos.authGSSClientInit(service)
        try:
            kerberos.authGSSClientStep(krb_context, "")
        except Exception as ex:
            print '{0}'.format(ex)
        self._krb_context = krb_context
        self.auth_header = ("Negotiate " + kerberos.authGSSClientResponse(krb_context))

    def verify_response(self, auth_header):
        # Handle comma-separated lists of authentication fields
        for field in auth_header.split(","):
            kind, __, details = field.strip().partition(" ")
            if kind.lower() == "negotiate":
                auth_details = details.strip()
                break
        else:
            raise ValueError("Negotiate not found in %s" % auth_header)
        krb_context = self._krb_context
        if krb_context is None:
            raise RuntimeError("Ticket already used for verification")
        self._krb_context = None
        kerberos.authGSSClientStep(krb_context, auth_details)
        kerberos.authGSSClientClean(krb_context)


def basic_auth(url):
    """
    Kerberos url opener for internal websites
    """
    global parse_output

    krb = KerberosTicket(kerberos_location)
    headers = {"Authorization": krb.auth_header}
    auth = HTTPBasicAuth(http_user, http_pass)

    #Ignore proxy to parse internal resources
    proxy = ""
    proxydict = {
        "http": proxy,
        "https": proxy,
        "ftp": proxy
    }

    try:
        r = requests.get(url, headers=headers, proxies=proxydict, timeout=100)

        if "Page not found" in r.content or "Authorization not granted" in r.content:
            r = requests.get(url, auth=auth, timeout=15)
            if debug:
                print '[%s] url: Page not found or Authorization not granted. Making request with basic auth' % url
        elif "Access Denied" in r.content:
            if debug:
                print '[%s] url: Access Denied' % url
            raise Exception('Access Denied: %s\n%s' % (url, r))
        elif "Authentication failed" in r.content:
            if debug:
                print '[%s] url: Authentication failed' % url
            raise Exception('Login failed: %s\n%s' % (url, r))
        else:
            if r.status_code != 200:
                if debug:
                    print '[%s] url: All was OK but return code is not 200' % url
                raise Exception('Got content, but response code was not 200 for: %s\n%s' % (url, r))

    except requests.exceptions.Timeout:
        if debug:
            print '[%s] url: Timeout error.' % url

    except UnboundLocalError:
        #Happens when webserver is down and we get 'page not found' error before timeout limit.
        if debug:
            print '[%s] url: UnboundLocalErrors' % url

    except Exception as ex:
        #General exception handler. Catch previous raise exception strings into "error" variable
        if debug:
            print '[%s] url: General exception occured. %s' % (url, '{0}'.format(ex))
    else:
        #If everything was ok, return r.content for future use
        parse_output = r.content
        return parse_output


def get_url_from_siteid(siteid, urls):
    krb = KerberosTicket(kerberos_location)
    headers = {"Authorization": krb.auth_header}
    proxy = ""
    proxydict = {
        "http": proxy,
        "https": proxy,
        "ftp": proxy
    }
    url = 'http://www.yoursite.net/idc/idcplg?IdcService=SS_GET_PAGE&siteId=' + siteid
    try:
        r = requests.get(url, headers=headers, proxies=proxydict, timeout=100)
        domain = urlparse.urlsplit(r.url)[1].split(':')[0]
        domain = 'http://' + domain

        if r.status_code == 404:
            request = urllib2.Request('http://www.yoursite.se/idc/idcplg?IdcService=SS_GET_PAGE&siteId=' + siteid)
            proxy_handler = urllib2.ProxyHandler({'http': 'http://domain\user:pass@proxy.site.net:port'})
            opener = urllib2.build_opener(proxy_handler)
            try:
                f_request = opener.open(request)
                domain = urlparse.urlsplit(f_request.geturl())[1].split(':')[0]
                domain = "http://" + domain
            except urllib2.HTTPError, err:
                domain = urlparse.urlsplit(err.url)[1].split(':')[0]

                if domain is not 'goodsite.net':
                    domain = "http://" + domain
                else:
                    if err.code == 404:
                        domain = '404_error'
                    else:
                        domain = 'None'
    except:
        domain = 'error'

    counter = 0
    for each_url in urls:
        if siteid == each_url[1]:
            each_url.append(domain)
            urls[counter] = each_url
            break
        counter = counter + 1


def get_editors():

    unique_editors = []

    ucm_publisher_roles = [
        'role1',
        'role2',
        'role3',
        'role4',
        'role5'
        ]

    chosen_roles = ''
    for each_ucm_role in ucm_publisher_roles:
        chosen_roles = each_ucm_role + '%2C' + chosen_roles

    basic_auth('this_link_should_return_table_with_user_and_roles' + chosen_roles)
    '''
    Example of table:
    
    	  	<table class="table3 horisontal vertical framed" style="width:100%">
	  		<thead>
		  		<tr>
		  			<th>Roles</th>
		  			<th>Users</th>
		  		</tr>
	  		</thead>
	  		<tbody>
			<tr>
				<td>admin</td>
				<td>
					  user<br />
						user<br />
						user<br />
				</td>
			</tr>
			</tbody>
	  </table>
    '''
    output_soup = BeautifulSoup(parse_output)
    table = output_soup.findAll("table", {"class": "table3 horisontal vertical framed"})

    for each_tr in table:
        rows = each_tr.findAll("tr")
        for row in rows:
            tds = row.findAll("td")
            for each_td in tds:
                if len(each_td) == 1:
                    ucm_role = each_td.contents[0]
                else:
                    ucm_role_counter = 0
                    for x in each_td:
                        if len(x) > 5:
                            unique_editors.append(x)
                            ucm_role_counter = ucm_role_counter + 1

                    print "%s;%s" % (ucm_role, ucm_role_counter)

    print "Total number of editors;", len(set(unique_editors))


def analyze_project_file(siteid, filename, search_string, urls):
    """
    WCM project file analyzer. Allows to search for strings and count their amount.
    Result is written into urls array
    """

    with open(filename, "r") as xml_file:
        xml_file_content = xml_file.read()

    if search_string in xml_file_content:
        counter = 0
        for each_url in urls:
            if siteid == each_url[1]:
                each_url.append('Yes')
                urls[counter] = each_url
                break
            counter = counter + 1

        with open(filename, "r") as xml_file:
            search_string_counter = 0
            for each_line in xml_file:
                if search_string in each_line:
                    search_string_counter = search_string_counter + 1
            counter = 0
            for each_url in urls:
                if siteid == each_url[1]:
                    each_url.append(search_string_counter)
                    urls[counter] = each_url
                    break
                counter = counter + 1
    else:
        counter = 0
        for each_url in urls:
            if siteid == each_url[1]:
                each_url.append('No')
                each_url.append('0')
                urls[counter] = each_url
                break
            counter = counter + 1


def get_site_info(siteid, urls):
    pages = []
    objects = []
    basic_auth('http://your.wcm.site/idc/idcplg?IdcService=SS_GET_SITE_REPORT&siteId=%s&sitesList=7' % siteid)
    output_soup = BeautifulSoup(parse_output)
    table = output_soup.findAll("table", {"id": "NodeLayouts"})
    for each_tr in table:
        rows = each_tr.findAll("tr")
        for row in rows:
            tds = row.findAll("td")
            for each_td in tds:
                ahref_counter = 0
                for each_ahref in each_td.findAll('a', href=True):
                    ahref_string = u'%s' % (each_ahref.contents[0])
                    if len(ahref_string) > 1:
                        ahref_counter = ahref_counter + 1
                pages.append(ahref_counter)
    total_pages = sum(pages)

    table = output_soup.findAll("table", {"id": "UrlDataFiles"})
    for each_tr in table:
        rows = each_tr.findAll("tr")
        for row in rows:
            tds = row.findAll("td")
            for each_td in tds:
                object_counter = 0
                for each_ahref in each_td.findAll("div", {"class": "xuiDisplayText_Sm"}):
                    object_id = u'%s' % (each_ahref.contents[0])
                    if len(object_id) > 1:
                        object_counter = object_counter + 1
                objects.append(object_counter)

    total_objects = sum(objects)
    
    counter = 0
    for each_url in urls:
        if siteid == each_url[1]:
            each_url.append(total_pages)
            each_url.append(total_objects)
            urls[counter] = each_url
            break
        counter = counter + 1


def count_news(each_month):
    if each_month <= now.month:
        max_days_in_month = monthrange(2014, each_month)[1]
        for each_security_group in ['type1', 'type2']:
            basic_auth(
               http://path_to_search_query
            )
            output_soup = BeautifulSoup(parse_output)
            table = output_soup.findAll("table", {"class": "xuiPopupTable"})
            print '%s News in %s, 2014: %s' % (each_security_group, calendar.month_name[each_month], len(table))


def mutate_list(listproxy, value_to_add):
    mutant = listproxy
    mutant.append(value_to_add)
    listproxy = mutant


def assign_project_file(project_file, urls):

    with open(project_file, "r") as xml_file:
        xml_file_content = xml_file.read()

    find_ucmid_in_xml = re.compile(r'siteId="(\w+)"')
    siteid_in_project_file = re.search(find_ucmid_in_xml, xml_file_content)

    if siteid_in_project_file:
        if siteid_in_project_file.group(1) in [each_url[1] for each_url in urls]:
            counter = 0
            for each_url in urls:
                if siteid_in_project_file.group(1) == each_url[1]:
                    if len(each_url) < 7:
                        each_url.append(project_file)
                        urls[counter] = each_url
                    else:
                        print '%s already has project file %s' % (siteid_in_project_file.group(1), project_file)
                    break

                counter = counter + 1
        else:
            print 'Could not find %s in urls array' % siteid_in_project_file.group(1)
    else:
        print 'Could not find siteid in', project_file

if __name__ == '__main__':
    mgr = multiprocessing.Manager()
    urls = mgr.list([])
    basic_auth('http://your_ucm_site/idc/idcplg?IdcService=SS_GET_SITES_ADMIN_PAGE')
    #=============================================================================================================
    temp_array = []
    for each_log_line in parse_output.splitlines(True):

        if "site.index" in each_log_line:
            temp_array.append('%s' % each_log_line.split("=")[1].translate(None, ';"').rstrip().strip())
        if 'site.siteId' in each_log_line:
            temp_array.append('%s' % each_log_line.split("=")[1].translate(None, ' ;"').rstrip())
        if 'site.siteLabel' in each_log_line:
            temp_array.append('%s' % each_log_line.split("=")[1].translate(None, ';"').rstrip())
        if "site.isStopped" in each_log_line:
            temp_array.append('%s' %  each_log_line.split("=")[1].translate(None, ' ;"').rstrip())
        if "site.siteUrl +=" in each_log_line:
            temp_array.append('%s' %  each_log_line.split("+=")[1].translate(None, ' ;"').rstrip())
            mutate_list(urls, temp_array)
            temp_array = []

    print '[%s] Array is done in %s' % (datetime.datetime.now(), (datetime.datetime.now()-startTime))
    #=============================================================================================================
    temp_time = datetime.datetime.now()
    get_site_url_jobs = [
        multiprocessing.Process(
            target=get_url_from_siteid,
            args=(each_url[1], urls)
        )
        for each_url in urls
    ]
    for j in get_site_url_jobs:
        j.start()
    for j in get_site_url_jobs:
        j.join()

    print '[%s] get_site_url_jobs is done in %s' % (datetime.datetime.now(), (datetime.datetime.now()-temp_time))
    #=============================================================================================================
    temp_time = datetime.datetime.now()
    find_all_xmls = [
        os.path.join(root_dir, f)
        for root_dir, sub_dirs, filename in os.walk(find_weblayout)
        for f in filename
        if os.path.splitext(f)[1] == '.xml'
    ]
    assign_project_file_jobs = [
        multiprocessing.Process(
            target=assign_project_file,
            args=(each_xml, urls)
        )
           for each_xml in find_all_xmls
    ]
    for j in assign_project_file_jobs:
        j.start()
    for j in assign_project_file_jobs:
        j.join()
    print '[%s] assign_project_file_jobs is done in %s' % (datetime.datetime.now(), (datetime.datetime.now()-temp_time))
    #=============================================================================================================
    temp_time = datetime.datetime.now()
    for each_search_string in ['campaign', 'Site="true"']:
        analyze_project_file_jobs = [
            multiprocessing.Process(
                target=analyze_project_file,
                args=(each_url[1], each_url[6], each_search_string, urls)
            )
            for each_url in urls
        ]
        for j in analyze_project_file_jobs:
            j.start()
        for j in analyze_project_file_jobs:
            j.join()
    print '[%s] analyze_project_file_jobs is done in %s' % (datetime.datetime.now(), (datetime.datetime.now()-temp_time))
    #=============================================================================================================
    temp_time = datetime.datetime.now()
    get_site_info_jobs = [
        multiprocessing.Process(
            target=get_site_info,
            args=(each_url[1], urls)
        )
        for each_url in urls
    ]
    def split_seq(seq, numPieces):
        newseq = []
        splitsize = 1.0/numPieces*len(seq)
        for i in range(numPieces):
                newseq.append(seq[int(round(i*splitsize)):int(round((i+1)*splitsize))])
        return newseq
    for each_array in split_seq(get_site_info_jobs, 5):
        for j in each_array:
            j.start()
        for j in each_array:
            j.join()
    print '[%s] get_site_info_jobs is done in %s' % (datetime.datetime.now(), (datetime.datetime.now()-temp_time))
    #=============================================================================================================
    print urls
    print 'Site index;Site id;Site name;Is active;Path to site in WCM tool;Link to live site;Has campaign;Amount of Campaigns;Has subsites;Amount of Subsites;Total Pages;Total objects'

    for each_url in urls:
        site_index = each_url[0]
        site_id = each_url[1]
        site_label = each_url[2]
        site_state = each_url[3]
        site_url = "http://path_to_site" + each_url[4]
        site_domain = each_url[5]
        site_xml = each_url[6]
        find_top_domain = re.compile('(?:\.)([^\.]{1,3}\.?[^\.]*)$')
        top_level_domain = re.search(find_top_domain, site_domain)

        if top_level_domain:
            if top_level_domain.group(1) == 'net':
                internal = internal + 1
            else:
                external = external + 1
        else:
            unknown = unknown + 1

        campaign_site = each_url[7]
        campaign_count = each_url[8]
        subsite = each_url[9]
        subsite_count = each_url[10]
        total_pages = each_url[11]
        total_objects = each_url[12]

        print '%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s' % (site_index, site_id, site_label.decode('unicode-escape'), site_state, site_url, site_domain,
            campaign_site, campaign_count, subsite, subsite_count, total_pages, total_objects)

    print 'Internal websites:',internal
    print 'External websites:',external
    print 'Unknown:',unknown
    print 'Total websites:',len(urls)
    get_editors()
    #=============================================================================================================
    temp_time = datetime.datetime.now()
    count_news_jobs = [
        multiprocessing.Process(
            target=count_news,
            args=(each_month,)
        )
           for each_month in range(1, 13)
    ]
    for j in count_news_jobs:
        j.start()
    for j in count_news_jobs:
        j.join()
    print '[%s] count_news_jobs is done in %s' % (datetime.datetime.now(), (datetime.datetime.now()-temp_time))
    #=============================================================================================================
    print '[%s] Total time: in %s' % (datetime.datetime.now(), (datetime.datetime.now()-startTime))
