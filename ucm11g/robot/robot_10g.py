# -*- coding: utf-8 -*-
import sys
import multiprocessing
from multiprocessing import Manager
import requests
import os
import re
import kerberos_sspi as kerberos
import win32com.client as win32
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import unicodedata
import time
import cx_Oracle
import datetime
import traceback


#==================================================================================================================================
#===================================================== Variables ==================================================================
kerberos_location = "HTTP@opensso.company.net"
http_user = '123'
http_pass = '456'

skip_timeout_urls = {
                    'http://bad_host.com',
                    'moreb_http_bad_host'
                    }
#send robot reports to:
email_address = 'email_report@report.net'

#ip address of webserver, where to store reports
ip_address = 'ip_address_of_local_machine:port?'

#main config
ucm_servers = \
    [
        #1
        ['hostname', 'shortname', 'dbhostane', 'db_port', 'db_sid', 'db_name', 'db_pass',
            ['cluster_ip_1', 'cluster_ip_2', 'cluster_ip_3', 'cluster_ip_4'],
            ['balancer_tag_1', 'balancer_tag_2', 'balancer_tag_3']
        ],
        #2
        ['hostname', 'shortname', 'dbhostane', 'db_port', 'db_sid', 'db_name', 'db_pass',
            ['cluster_ip_1', 'cluster_ip_2', 'cluster_ip_3', 'cluster_ip_4'],
            ['balancer_tag_1', 'balancer_tag_2', 'balancer_tag_3']
        ],

    ]


#===================================================== Variables =====================================================================
#=====================================================================================================================================

global log_file_errors
global email_report
global current_date

#debug switch True/False
debug = False
#Show completion times for each function. Good for troubleshooting long running times.
show_times = False

if debug:
    print 'Starting script in debug mode'

class KerberosTicket:
    def __init__(self, service):
        __, krb_context = kerberos.authGSSClientInit(service)
        try:
            kerberos.authGSSClientStep(krb_context, "")
        except Exception as ex:
            error = '{0}'.format(ex)
            send_mail('Kerberos error: %s' % error, email_report, log_file_errors)
            time.sleep(600)
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
            send_mail("Negotiate not found in %s" % auth_header, email_report, log_file_errors)
            raise ValueError("Negotiate not found in %s" % auth_header)

        krb_context = self._krb_context
        if krb_context is None:
            send_mail("Ticket already used for verification", email_report, log_file_errors)
            raise RuntimeError("Ticket already used for verification")
        self._krb_context = None
        kerberos.authGSSClientStep(krb_context, auth_details)
        kerberos.authGSSClientClean(krb_context)


def basic_auth(sendmail, sendmail_messages, log_file_errors, url, idc_basic_index=None):

    auth_sendmail = sendmail
    auth_sendmail_messages = sendmail_messages
    auth_errors = log_file_errors

    if debug:
        print '[%s] launching function basic_auth with params:' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print '\tauth_sendmail = %s\n' \
              '\tauth_sendmail_messages = %s\n' \
              '\tauth_errors = %s\n' \
              '\turl = %s\n' \
              '\tidc_basic_index = %s\n' \
              % (auth_sendmail, auth_sendmail_messages, auth_errors, url, idc_basic_index)

    global parse_output

    krb = KerberosTicket(kerberos_location)
    headers = {"Authorization": krb.auth_header}
    auth = HTTPBasicAuth(http_user, http_pass)

    #Ignore proxy.
    proxy = ""
    proxyDict = {
        "http"  : proxy,
        "https" : proxy,
        "ftp"   : proxy
    }

    #Repeat this process 3 times.
    http_attempts = 0
    while http_attempts < 3:

        if debug:
            print '[%s] url: %s \n\tattempt: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url, http_attempts)

        if url in skip_timeout_urls:
            #some URL's won't open by default - pass those right away to increase script runtime
            if debug:
                print '[%s] url: %s. Found in timeout URLs - SKIP' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url)
            break
        else:
            try:
                #First, make a GET request using kerberos authentication
                r = requests.get(url, headers=headers, proxies=proxyDict, timeout=15)
                #If kerberos authentication failed, use basic auth
                if "Page not found" in r.content or "Authorization not granted" in r.content:
                    if debug:
                        print '[%s] url: %s. Page not found or Authorization not granted. Making request with basic auth'\
                              % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url)
                    r = requests.get(url, auth=auth, timeout=15)
                #Handle exceptions from here:
                elif "Access Denied" in r.content:
                    if debug:
                        print '[%s] url: %s. Access Denied'\
                              % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url)
                    raise Exception('Access Denied: %s\n%s' % (url, r))
                elif "Authentication failed" in r.content:
                    if debug:
                        print '[%s] url: %s. Authentication failed'\
                              % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url)
                    raise Exception('Login failed: %s\n%s' % (url, r))
                else:
                    if r.status_code != 200:
                        if debug:
                            print '[%s] url: %s. All was OK but return code is not 200'\
                                  % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url)
                        raise Exception('Got content, but response code was not 200 for: %s\n%s' % (url, r))

            except requests.exceptions.Timeout:

                if debug:
                    print '[%s] url: %s. Timeout error. Attempt: %s'\
                          % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url, http_attempts)
                #print 'timeout', url
                #HTTP request takes longer than 15 seconds to open a website
                #auth_errors.append('%s: Timeout error for URL: %s' % (idc_basic_index, url))
                if http_attempts == 2:
                    if debug:
                        print '[%s] url: %s. should be attempt 2: %s. 3x timeout errors - quit.'\
                              % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url, http_attempts)
                    #print '3 timeouts == sendmail'
                    parse_output = False
                    auth_sendmail.value = True
                    auth_sendmail_messages.append('3 attempts - %s: Timeout error for URL: %s' % (idc_basic_index, url))
            except UnboundLocalError:
                #Happens when webserver is down and we get 'page not found' error before timeout limit.
                if debug:
                    print '[%s] url: %s. UnboundLocalError. Attempt: %s'\
                          % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url, http_attempts)
                if http_attempts == 2:
                    if debug:
                        print '[%s] url: %s. should be attempt 2: %s. 3x UnboundLocalError - quit.'
                    parse_output = False
                    auth_sendmail.value = True
                    auth_sendmail_messages.append('3 attempts - %s: No response from : %s' % (idc_basic_index, url))
                    auth_errors.append('3 attempts - %s: No response from: %s' % (idc_basic_index, url))
            except Exception as ex:
                #General exception handler. Catch previous raise exception strings into "error" variable
                if debug:
                    print '[%s] url: %s. General exception occured. Attempt: %s'\
                        % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url, http_attempts)
                if http_attempts == 2:
                    if debug:
                        print '[%s] url: %s. General exception occured. Attempt: %s'\
                            % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url, http_attempts)
                    parse_output = False
                    error = '{0}'.format(ex)
                    auth_sendmail.value = True
                    auth_sendmail_messages.append('3 attempts - Bad url: %s. Error %s' % (url, error))
                    auth_errors.append('3 attempts - Bad url: %s. Error %s' % (url, error))
            else:
                #If everything was ok, return r.content for future use
                parse_output = r.content
                return parse_output
            finally:
                #Increase number of http attempts
                #Wait 60 seconds before making a new request
                if debug:
                    print '[%s] url: %s. General exception occured. Sleeping for 60 seconds. Attempt: %s'\
                        % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url, http_attempts)
                http_attempts += 1
                #time.sleep(60)

    sendmail = auth_sendmail
    sendmail_messages = auth_sendmail_messages
    log_file_errors = auth_errors


def split(wordinput, size):
    #Function to split long strings into smaller parts for better view
    return [wordinput[start:start+size] + '<br>' for start in range(0, len(wordinput), size)]


def send_mail(msg, email_report, z):

    #Simple email sender. Must have MS outlook running

    log_file_errors = z
    if os.path.isfile(email_report):
        with open(email_report, "r") as myfile:
            data = myfile.read()
    else:
        data = ""

    open_file = open(email_report, 'w')
    message = '\n'.join(log_file_errors)
    open_file.write('\n%s\n%s' % (message, data))
    open_file.close()

    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.to = email_address
    mail.subject = 'Monitoring report'
    mail.Attachments.Add(email_report)
    mail.body = msg

    try:
        mail.send
    except Exception as ex:
        error = '{0}'.format(ex)
        log_file_errors.append('Cant send email. Error: %s' % error)

    z = log_file_errors

    time.sleep(timesleep)


def create_header(fname, current_date, current_time):
    open_file = open(fname, 'ab')
    open_file.write('<!DOCTYPE html> \
    \n<html> \
    \n<head> \
    \n<link href="/style.css" rel="stylesheet" type="text/css"> \
    \n</head> \
    \n<body> \
    \n<script type="text/javascript" language="javascript" src="/script.js"></script> \
    \n<p><a href=http://' + ip_address + "/reports/report_" + current_date + ".txt"'>Report here</a> </p>\
    \n<font color="#000080"><strong>Content Server Log File. Created: ' + current_date + '<span id="timer"> ' + current_time + ' \
    </span></strong></font> \
    \n<font color="#000080"><strong><p>Script run last time: <span id="countdown"> </span></p></strong></font> \
    \n<table>')
    open_file.close()


def create_footer(fname):
    open_file = open(fname, 'ab')
    open_file.write('\n</table> \
    \n</body> \
    \n</html>')
    open_file.close()


def check_db(sendmail, sendmail_messages, log_file_errors, idc_prefix, db_ip, db_port, db_sid, db_user, db_pass):

    database_time = datetime.datetime.now()
    #print 'Starting check_db for ', idc_prefix
    db_sendmail = sendmail
    db_sendmail_messages = sendmail_messages
    db_errors = log_file_errors

    if idc_prefix == 'dev' or idc_prefix == 'test':
        try:
            db_con = cx_Oracle.connect('%s/%s@%s:%s/%s' % (db_user, db_pass, db_ip, db_port, db_sid))
            cursor = db_con.cursor()
            #Overall items in the queue waiting for publishing
            sql1 = u'select count(*) from REVISIONS where DSTATUS=' + "'GENWWW'"
            #Items which failed during indexing
            sql2 = u'select * from REVISIONS where dmessage=' + "'!csIndexingFailed'" + \
                'and dprocessingstate=' "'F'" + 'and dreleasestate=' + "'N'"

            cursor.execute(sql1)
            row = cursor.fetchone()
            doc_number = row[0]

            cursor.execute(sql2)
            failed_rows = cursor.fetchall()
            if failed_rows:
                for each_failed_row in failed_rows:
                    print "%s: %s" % (idc_prefix, each_failed_row)

            cursor.close()
            db_con.close()

            if doc_number > 20:
                db_sendmail.value = True
                db_sendmail_messages.append('%s: Too many documents in the queue: %s' % (idc_prefix, doc_number))
                db_errors.append('%s: Too many documents in the queue: %s' % (idc_prefix, doc_number))

        except Exception as ex:
            db_error = '{0}'.format(ex)
            db_sendmail.value = True
            db_errors.append('%s: database error occured: %s' % (idc_prefix, db_error))
            db_sendmail_messages.append('%s: database error occured: %s' % (idc_prefix, db_error))
    else:
        try:
            db_tns = cx_Oracle.makedsn(db_ip, db_port, db_sid)
            db_con = cx_Oracle.connect(db_user, db_pass, db_tns)

            cursor = db_con.cursor()
            #--------------------------------------------------------------------------------#
            #Overall items in the queue waiting for publishing
            if idc_prefix == 'contrib':
                sql1 = u'select count(*) from REVISIONS where DSTATUS=' + "'DONE'"
                cursor.execute(sql1)
                sql1_rows = cursor.fetchone()
                if sql1_rows[0] > 20:
                    db_sendmail.value = True
                    #print 'db_sendmail'
                    db_errors.append('%s: Too many documents in the queue: %s' % (idc_prefix, sql1_rows[0]))
                    db_sendmail_messages.append('%s: Too many documents in the queue: %s' % (idc_prefix, sql1_rows[0]))
            #--------------------------------------------------------------------------------#
            #Items which failed during indexing process
            sql2 = u'select * from REVISIONS where dmessage=' + "'!csIndexingFailed'" + \
                         'and dprocessingstate=' "'F'" + 'and dreleasestate=' + "'N'"
            cursor.execute(sql2)
            failed_rows = cursor.fetchall()
            if failed_rows:
                for each_failed_row in failed_rows:
                    print "%s: %s" % (idc_prefix, each_failed_row)
            #--------------------------------------------------------------------------------#
            #Items which are waiting for IBR connection:
            sql3 = u'select count(*) from REVISIONS where DSTATUS=' + "'GENWWW'" + \
                   'and DRELEASESTATE=' "'N'" + 'and DPROCESSINGSTATE=' + "'C'" + 'and DINDEXERSTATE=' + "' '"
            cursor.execute(sql3)
            sql3_rows = cursor.fetchone()
            if sql3_rows[0] > 10:
                db_sendmail.value = True
                db_errors.append('%s: too many items waiting for IBR %s' % (idc_prefix, sql3_rows[0]))
                db_sendmail_messages.append('%s: too many items waiting for IBR %s' % (idc_prefix, sql3_rows[0]))
            else:
                sql3_1 = u'select ddocname, dindate from REVISIONS where DSTATUS=' + "'GENWWW'" + \
                    'and DRELEASESTATE=' "'N'" + 'and DPROCESSINGSTATE=' + "'C'" + 'and DINDEXERSTATE=' + "' '"
                cursor.execute(sql3_1)
                sql3_1_rows = cursor.fetchall()
                for each_content_id in sql3_1_rows:
                    content_id = each_content_id[0]
                    dindate = each_content_id[1]
                    time_difference = (datetime.datetime.now() - datetime.timedelta(hours=1)) - dindate
                    if int(time_difference.total_seconds()) > 1800:
                        db_sendmail.value = True
                        db_errors.append('%s: %s item takes too long to render %s' % (idc_prefix, content_id, time_difference))
                        db_sendmail_messages.append('%s: %s item takes too long to render %s' % (idc_prefix, content_id, time_difference))
            #--------------------------------------------------------------------------------#
            #Powerpoint files
            sql4 = u'select ddocname from REVISIONS where dmessage like' + "'%failure%'" + \
                'and dprocessingstate=' "'F'" + 'and dreleasestate=' + "'N'"
            cursor.execute(sql4)
            sql4_rows = cursor.fetchall()
            if sql4_rows:
                for each_failed_file in sql4_rows:
                    print "PowerPointX failed file: %s: %s" % (idc_prefix, each_failed_file)

            cursor.close()
            db_con.close()
        except Exception as ex:
            db_error = '{0}'.format(ex)
            db_sendmail.value = True
            db_errors.append('%s: database error occured: %s' % (idc_prefix, db_error))
            db_sendmail_messages.append('%s: database error occured: %s' % (idc_prefix, db_error))

    sendmail = db_sendmail
    sendmail_messages = db_sendmail_messages
    log_file_errors = db_errors
    if show_times == True:
        print '%s Finished checkdb job in %s' %(idc_prefix, (datetime.datetime.now()-database_time))


def check_nodes(sendmail, sendmail_messages, log_file_errors, idc_prefix, nodes):
    checknodes_time = datetime.datetime.now()
    #print 'Starting check_nodes for ', idc_prefix
    node_sendmail = sendmail
    node_sendmail_messages = sendmail_messages
    node_errors = log_file_errors
    #Open URL and search for this string:
    string_to_find = 'string'

    if idc_prefix == 'contrib' or idc_prefix == 'intra':
        for each_node in nodes:
            #print 'checking node:', each_node
            if idc_prefix == 'contrib':
                url = 'http://' + each_node + '/path/index.htm'
                basic_auth(sendmail, sendmail_messages, log_file_errors, url, idc_prefix)
            if idc_prefix == 'intra':
                url = 'http://' + each_node + '/path/index.htm'
                basic_auth(sendmail, sendmail_messages, log_file_errors, url, idc_prefix)
            if parse_output:
                if parse_output.find(string_to_find) == -1:
                    #couldn't find 'string_to_find'
                    node_sendmail.value = True
                    node_sendmail_messages.append('%s node %s: error. Could not find string - %s' % (idc_prefix, each_node, string_to_find))
                    node_errors.append('%s node %s: error. Could not find string - %s' % (idc_prefix, each_node, string_to_find))


    sendmail = node_sendmail
    sendmail_messages = node_sendmail_messages
    node_errors = node_errors
    if show_times == True:
        print '%s Finished checknodes job in %s' % (idc_prefix, (datetime.datetime.now()-checknodes_time))


def parse_providers(sendmail, sendmail_messages, log_file_errors, idc_prefix, idc_link):
    #print 'Starting parse providers for ', idc_prefix
    parse_providers_time = datetime.datetime.now()
    providers_sendmail = sendmail
    providers_sendmail_messages = sendmail_messages
    providers_errors = log_file_errors

    url = 'http://' + idc_link + '/idc/idcplg?IdcService=GET_ALL_PROVIDERS'
    basic_auth(sendmail, sendmail_messages, log_file_errors, url, idc_prefix)


    #print parse_output
    if parse_output:
        output_soup = BeautifulSoup(parse_output)
        table = output_soup.findAll("table", {"id": "table_0"})

        if idc_prefix == "dev" or idc_prefix == "test":
            #print 'is %s' % idc_prefix
            if table:
                for each_tr in table:
                    rows = each_tr.findAll("tr")
                    for row in rows:
                        tds = row.findAll("td")
                        provider_name = tds[0].text.strip('\n').strip()
                        provider_test = tds[10]
                        to_string = u'%s' % provider_test
                        fixed_text = unicodedata.normalize('NFKD', to_string).encode('ascii', 'ignore')
                        match = re.findall(r'href="/idc/idcplg\?IdcService=TEST_PROVIDER(.*)"', fixed_text)
                        if match:
                            #print match
                            provider_test_url = "http://%s/idc/idcplg?IdcService=TEST_PROVIDER&pName=%s" % (idc_link, provider_name)
                            #press refresh "test" button
                            basic_auth(sendmail, sendmail_messages, log_file_errors, provider_test_url, idc_prefix)

                #print after test is finished, make a new request to check the provider status result
                basic_auth(sendmail, sendmail_messages, log_file_errors, url, idc_prefix)
                output_soup = BeautifulSoup(parse_output)
                table = output_soup.findAll("table", {"id": "table_0"})

                if table:
                    for each_tr in table:
                        rows = each_tr.findAll("tr")
                        for row in rows:
                            tds = row.findAll("td")
                            provider_name = tds[0].text.strip('\n').strip()
                            provider_state = tds[6].text.strip('\n').strip()
                            if provider_state is "down":
                                providers_sendmail.value = True
                                providers_sendmail_messages.append("%s: provider %s is down" % (idc_prefix, provider_name))
                                providers_errors.append("%s: provider %s is down" % (idc_prefix, provider_name))
                            for each_word in provider_state.split():
                                if each_word == '0':
                                    providers_sendmail.value = True
                                    providers_sendmail_messages.append("%s: provider %s has 0 connections" % (idc_prefix, provider_name))
                                    providers_errors.append("%s: provider %s has 0 connections" % (idc_prefix, provider_name))

                else:
                    providers_errors.append('%s: Could not find providers table. %s' % (idc_prefix, url))
                    send_mail('%s: Could not find providers table. %s' % (idc_prefix, url), email_report, log_file_errors)
            else:
                providers_errors.append('%s: Could not find providers table. %s' % (idc_prefix, url))
                send_mail('%s: Could not find providers table. %s' % (idc_prefix, url), email_report, log_file_errors)
        else:
            #print idc_prefix
            if table:
                for each_tr in table:
                    rows = each_tr.findAll("tr")
                    for row in rows:
                        tds = row.findAll("td")
                        provider_name = tds[0].text.strip('\n').strip()
                        provider_state = tds[6].text.strip('\n').strip()
                        #print provider_state
                        if provider_state == "down":
                            #print "IS DOWN"
                            providers_sendmail.value = True
                            providers_sendmail_messages.append("%s: provider %s is down" % (idc_prefix, provider_name))
                            providers_errors.append("%s: provider %s is down" % (idc_prefix, provider_name))
                        for each_word in provider_state.split():
                            if each_word == '0':
                                providers_sendmail.value = True
                                providers_sendmail_messages.append("%s: provider %s has 0 connections" % (idc_prefix, provider_name))
                                providers_errors.append("%s: provider %s has 0 connections" % (idc_prefix, provider_name))
            else:
                providers_sendmail.value = True
                providers_sendmail_messages.append('%s: Could not find providers table. %s' % (idc_prefix, url))
                providers_errors.append('%s: Could not find providers table. %s' % (idc_prefix, url))

        sendmail = providers_sendmail
        sendmail_messages = providers_sendmail_messages
        log_file_errors = providers_errors
    if show_times == True:
        print '%s Finished parseproviders job in %s' % (idc_prefix, (datetime.datetime.now()-parse_providers_time))


def special_error_parser(sendmail, sendmail_messages, log_file_errors, idc_prefix, special_error_data, error_type, content_errors_check, i):

    special_error_parser_sendmail = sendmail
    special_error_parser_sendmail_messages = sendmail_messages
    special_error_parser_errors = log_file_errors
    content_errors_list = content_errors_check

    # Function to analyze errors from content server logs.
    # Sometimes a bad error occurs and we need to track if it was reported before.
    # We check for error type and time it was reported.
    # If time already exists, it means the error was already reported.
    # Currently, we track errors with strings:
    # 1. "started" (when content server was restarted)
    # 2. "Server down"
    # 3. "memory" (when there is a message in the logs indicating about memory problems

    if special_error_data not in content_errors_list[i]:
        content_errors_list[i].append(special_error_data)
        special_error_parser_sendmail_messages.append('%s Special type error: %s' % (idc_prefix, error_type))
        special_error_parser_errors.append('%s Special type error: %s' % (idc_prefix, special_error_data))
        special_error_parser_sendmail.value = True


    sendmail = special_error_parser_sendmail
    sendmail_messages = special_error_parser_sendmail_messages
    log_file_errors = special_error_parser_errors
    content_errors_check = content_errors_list


def content_logs(sendmail, sendmail_messages, log_file_errors, idc_prefix, content_url, idc_link, current_date, current_time, content_errors_check, i):
    content_logs_times = datetime.datetime.now()
    #print 'Starting content logs for ', idc_prefix
    #True/False - send email report or not.
    content_sendmail = sendmail
    #List to hold information what we send in the email
    content_sendmail_messages = sendmail_messages
    #List to hold infromation what we write in the report txt file
    content_errors = log_file_errors
    temp_content_errors = []
    #List to hold old errors (so we don't report the same error)
    content_errors_list = content_errors_check[0]
    content_errors_rows = content_errors_check[1]
    basic_auth(sendmail, sendmail_messages, log_file_errors, content_url, idc_prefix)


    err_0 = 0
    err_1 = 0
    err_2 = 0
    err_3 = 0
    err_4 = 0
    err_5 = 0
    err_6 = 0
    err_7 = 0
    err_8 = 0
    err_9 = 0
    err_10 = 0
    err_11 = 0
    err_12 = 0
    err_13 = 0
    err_14 = 0

    if parse_output:
        if parse_output.find(current_date) == -1:
            if idc_prefix == 'contrib' or idc_prefix == 'intra' or idc_prefix == 'cons':
                content_sendmail.value = True
                content_sendmail_messages.append('%s content: No content log file found' % idc_prefix)
                content_errors.append('%s content: No content log file found' % idc_prefix)
                content_errors.append('')
            else:
                content_sendmail_messages.append('%s content: No content log file found' % idc_prefix)
                content_errors.append('%s content: No content log file found' % idc_prefix)
                content_errors.append('')
        else:
            fname = 'D:/apache2/Apache2/htdocs/' + idc_prefix + '/content_' + current_date + '.html'
            url_fname = ip_address + '/' + idc_prefix + '/content_' + current_date + '.html'

            if os.path.isfile(fname):
                with open(fname, "r") as myfile:
                    previous_data = myfile.read()
            else:
                previous_data = False
                create_header(fname, current_date, current_time)

            log_counter = 0

            #variable k is required to remember rows in content log file
            k = 0

            for each_log_line in parse_output.splitlines(True):
                if log_counter == 0:
                    log_url = BeautifulSoup(each_log_line)
                    my_regex = r"" + re.escape(current_date)

                    if re.search(my_regex, each_log_line, re.IGNORECASE):
                        log_counter = 1

                        for ahref in log_url.findAll('a', href=True):
                            log_link = ahref['href']
                            log_url = 'http://' + idc_link + '/idc/groups/secure/logs/' + log_link
                            basic_auth(sendmail, sendmail_messages, log_file_errors, log_url, idc_prefix)

                            if len(content_errors_rows[i]) == 0:
                                for line_in_log in parse_output.splitlines(True):
                                    k += 1

                                    ldap_soup = BeautifulSoup(line_in_log)
                                    for error_loop in ldap_soup.findAll('tr'):
                                        error_type = error_loop.contents[0].text
                                        error_date = error_loop.contents[1].text
                                        error_data = error_loop.contents[2].text
                                        #error_data = ''.join(split(error_loop.contents[2].text, 240)).replace("[ Details ]", "")

                                        if "error_1" in error_data:
                                            err_1 += 1
                                            #continue
                                        elif "error_" in error_data:
                                            err_2 += 1
                                            #continue
                                        elif "error_3" in error_data:
                                            err_3 += 1
                                            #continue
                                        elif "error_4" in error_data:
                                            err_4 += 1
                                            #continue
                                        elif "error_5" in error_data:
                                            err_5 += 1
                                            #continue
                                        elif "error_6" in error_data:
                                            err_6 += 1
                                            #continue
                                        elif "error7" in error_data:
                                            err_7 += 1
                                            #continue
                                        elif "error_8" in error_data:
                                            err_9 += 1
                                            #continue
                                        elif "error_9" in error_data:
                                            err_10 += 1
                                            #continue
                                        elif "error_10" in error_data:
                                            err_11 += 1
                                            #continue
                                        elif "error_11" in error_data:
                                            err_12 += 1
                                            #continue
                                        elif "error_12" in error_data:
                                            err_13 += 1
                                            #continue
                                        elif "error_13" in error_data:
                                            err_14 += 1
                                            #continue
                                        elif 'bad_error_1' in error_data:
                                            s = u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (error_type, error_date, error_data)
                                            encoded_text = s.encode('ascii', 'ignore')
                                            special_error_parser(sendmail, sendmail_messages, log_file_errors, idc_prefix, encoded_text, 'executed action', content_errors_list, i)
                                            temp_content_errors.append(encoded_text)
                                        elif 'bad_error_2' in error_data:
                                            s = u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (error_type, error_date, error_data)
                                            encoded_text = s.encode('ascii', 'ignore')
                                            special_error_parser(sendmail, sendmail_messages, log_file_errors, idc_prefix, encoded_text, 'SystemDatabase', content_errors_list, i)
                                            temp_content_errors.append(encoded_text)
                                            #content_open_file.write("\n" + encoded_text)
                                        elif 'bad_error_3' in error_data:
                                            s = u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (error_type, error_date, error_data)
                                            encoded_text = s.encode('ascii', 'ignore')
                                            special_error_parser(sendmail, sendmail_messages, log_file_errors, idc_prefix, encoded_text, 'Server Down', content_errors_list, i)
                                            temp_content_errors.append(encoded_text)
                                            #content_open_file.write("\n" + encoded_text)
                                        elif 'bad_error_4' in error_data:
                                            s = u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (error_type, error_date, error_data)
                                            encoded_text = s.encode('ascii', 'ignore')
                                            special_error_parser(sendmail, sendmail_messages, log_file_errors, idc_prefix, encoded_text, 'memory',content_errors_list, i)
                                            temp_content_errors.append(encoded_text)
                                            #content_open_file.write("\n" + encoded_text)
                                        else:
                                            err_0 += 1
                                            s = u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (error_type, error_date, error_data)
                                            encoded_text = s.encode('ascii', 'ignore')
                                            temp_content_errors.append(encoded_text)
                                            #content_open_file.write("\n" + encoded_text)
                            else:
                                for line_in_log in parse_output.splitlines(True):
                                    k += 1
                                    if k > content_errors_rows[i][len(content_errors_rows[i]) - 1]:
                                        ldap_soup = BeautifulSoup(line_in_log)
                                        for error_loop in ldap_soup.findAll('tr'):
                                            error_type = error_loop.contents[0].text
                                            error_date = error_loop.contents[1].text
                                            error_data = error_loop.contents[2].text
                                            #error_data = ''.join(split(error_loop.contents[2].text, 240)).replace("[ Details ]", "")

                                            if "error_1" in error_data:
                                                err_1 += 1
                                                #continue
                                            elif "error_2" in error_data:
                                                err_2 += 1
                                                #continue
                                            elif "error_3" in error_data:
                                                err_3 += 1
                                                #continue
                                            elif "error_4" in error_data:
                                                err_4 += 1
                                                #continue
                                            elif "error_5" in error_data:
                                                err_5 += 1
                                                #continue
                                            elif "error_6" in error_data:
                                                err_6 += 1
                                                #continue
                                            elif "error_7" in error_data:
                                                err_7 += 1
                                                #continue
                                            elif "error_8" in error_data:
                                                err_9 += 1
                                                #continue
                                            elif "error_9" in error_data:
                                                err_10 += 1
                                                #continue
                                            elif "error_10" in error_data:
                                                err_11 += 1
                                                #continue
                                            elif "error_11" in error_data:
                                                err_12 += 1
                                                #continue
                                            elif "error_12" in error_data:
                                                err_13 += 1
                                            elif "error_13" in error_data:
                                                err_14 += 1
                                                #continue
                                            elif 'bad_error_1' in error_data:
                                                s = u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (error_type, error_date, error_data)
                                                encoded_text = s.encode('ascii', 'ignore')
                                                special_error_parser(sendmail, sendmail_messages, log_file_errors, idc_prefix, encoded_text, 'executed action', content_errors_list, i)
                                                temp_content_errors.append(encoded_text)
                                                #content_open_file.write("\n" + encoded_text)
                                            elif 'bad_error_2' in error_data:
                                                s = u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (error_type, error_date, error_data)
                                                encoded_text = s.encode('ascii', 'ignore')
                                                special_error_parser(sendmail, sendmail_messages, log_file_errors, idc_prefix, encoded_text, 'SystemDatabase', content_errors_list, i)
                                                temp_content_errors.append(encoded_text)
                                                #content_open_file.write("\n" + encoded_text)
                                            elif 'bad_error_3' in error_data:
                                                s = u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (error_type, error_date, error_data)
                                                encoded_text = s.encode('ascii', 'ignore')
                                                special_error_parser(sendmail, sendmail_messages, log_file_errors, idc_prefix, encoded_text, 'Server Down', content_errors_list, i)
                                                temp_content_errors.append(encoded_text)
                                                #content_open_file.write("\n" + encoded_text)
                                            elif 'bad_error_4' in error_data:
                                                s = u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (error_type, error_date, error_data)
                                                encoded_text = s.encode('ascii', 'ignore')
                                                special_error_parser(sendmail, sendmail_messages, log_file_errors, idc_prefix, encoded_text, 'memory',content_errors_list, i)
                                                temp_content_errors.append(encoded_text)
                                                #content_open_file.write("\n" + encoded_text)
                                            else:
                                                err_0 += 1
                                                s = u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (error_type, error_date, error_data)
                                                encoded_text = s.encode('ascii', 'ignore')
                                                temp_content_errors.append(encoded_text)
                                                #content_open_file.write("\n" + encoded_text)
                else:
                    break

            content_errors_rows[i].append(k)
            #content_open_file.close()

            if err_1 != 0:
                content_errors.append('%s content: error_1: %s' % (idc_prefix, err_1))
            if err_2 != 0:
                content_errors.append('%s content: error_2: %s' % (idc_prefix, err_2))
            if err_3 != 0:
                content_errors.append('%s content: error_3: %s' % (idc_prefix, err_3))
            if err_4 != 0:
                content_errors.append('%s content: error_4: %s' % (idc_prefix, err_4))
            if err_5 != 0:
                content_errors.append('%s content: error_5: %s' % (idc_prefix, err_5))
            if err_6 != 0:
                content_errors.append('%s content: error_6: %s' % (idc_prefix, err_6))
            if err_7 != 0:
                content_errors.append('%s content: error_7: %s' % (idc_prefix, err_7))
            if err_9 != 0:
                content_errors.append('%s content: error_8: %s' % (idc_prefix, err_9))
            if err_10 != 0:
                content_errors.append('%s content: error_9: %s' % (idc_prefix, err_10))
            if err_11 != 0:
                content_errors.append('%s content: error_10: %s' % (idc_prefix, err_11))
            if err_12 != 0:
                content_errors.append('%s content: error_11: %s' % (idc_prefix, err_12))
            if err_13 != 0:
                content_errors.append('%s content: error_12: %s' % (idc_prefix, err_13))
            if err_14 != 0:
                content_errors.append('%s error_13: %s' % (idc_prefix, err_13))

            content_errors.append('%s content: Other errors: %s' % (idc_prefix, err_0))
            content_errors.append('%s content: Total errors: %s' % (idc_prefix, (int(err_0) + int(err_1) + int(err_2) + int(err_3) + int(err_4) +
            + int(err_5) + int(err_6) + int(err_7) + int(err_8) + int(err_9)) + int(err_10) + int(err_11) + int(err_11) + int(err_12) + int(err_13)))
            content_errors.append('Log location: http://%s' % url_fname)
            content_errors.append('')

            if previous_data and len(temp_content_errors) > 0:
                open_file = open(fname, 'w')
                message = '\n'.join(temp_content_errors)
                open_file.write('\n%s\n%s' % (message, previous_data))
                open_file.close()

            sendmail = content_sendmail
            sendmail_messages = content_sendmail_messages
            log_file_errors = content_errors
            content_errors_check[0] = content_errors_list
            content_errors_check[1] = content_errors_rows
    if show_times == True:
        print '%s Finished contentlogs job in %s' % (idc_prefix, (datetime.datetime.now()-content_logs_times))


def archiver_logs(sendmail, sendmail_messages, log_file_errors, idc_prefix, archiver_url, idc_link, i, current_date, current_time, archiver_errors):
    #print 'Starting archiver logs for ', idc_prefix
    archiver_logs_time = datetime.datetime.now()
    archiver_sendmail = sendmail
    archiver_sendmail_messages = sendmail_messages
    arch_errors = log_file_errors
    archiver_errors_list = archiver_errors[0]
    basic_auth(sendmail, sendmail_messages, log_file_errors, archiver_url, idc_prefix)

    err_0 = 0

    if parse_output:
        if parse_output.find(current_date) == -1:
            arch_errors.append('%s archiver: No archiver log file found' % idc_prefix)
            arch_errors.append('')
        else:
            aname = 'D:/apache2/Apache2/htdocs/' + idc_prefix + '/archiver_' + current_date + '.html'
            url_fname = ip_address + "/" + idc_prefix + "/archiver_" + current_date + ".html"

            if os.path.isfile(aname):
                os.remove(aname)

            arch_file = open(aname, 'ab')
            create_header(aname, current_date, current_time)
            log_counter = 0

            for each_log_line in parse_output.splitlines(True):
                if log_counter == 0:
                    log_url = BeautifulSoup(each_log_line)
                    my_regex = r"" + re.escape(current_date)
                    if re.search(my_regex, each_log_line, re.IGNORECASE):
                        log_counter = 1
                        for ahref in log_url.findAll('a', href=True):
                            log_link = ahref['href']
                            log_url = "http://" + idc_link + "/idc/groups/secure/logs/archiver/" + log_link
                            basic_auth(sendmail, sendmail_messages, log_file_errors, log_url, idc_prefix)
                            for line_in_log in parse_output.splitlines(True):
                                ldap_soup = BeautifulSoup(line_in_log)
                                for error_loop in ldap_soup.findAll('tr'):
                                    error_type = error_loop.contents[0].text
                                    error_date = error_loop.contents[1].text
                                    error_data = ''.join(split(error_loop.contents[2].text, 240)).replace("[ Details ]", "")

                                    err_0 += 1
                                    s = u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (error_type, error_date, error_data)
                                    encoded_text = s.encode('ascii', 'ignore')
                                    arch_file.write("\n" + encoded_text)
                else:
                    break
            arch_file.close()

            if err_0 > 1:
                if len(archiver_errors_list[i]) == 0:
                    archiver_errors_list[i].append(err_0)
                    archiver_sendmail.value = True
                    #print 'archiver_sendmail'
                    archiver_sendmail_messages.append('Found archiver errors: %s\nTotal errors: %s' % (idc_prefix, err_0))
                elif len(archiver_errors_list[i]) >= 1:
                    if err_0 > int(archiver_errors_list[i][int(len(archiver_errors_list[i]) - 1)]):
                        archiver_errors_list[i].append(err_0)
                        archiver_sendmail.value = True
                        #print 'archiver_sendmail'
                        archiver_sendmail_messages.append('Found archiver errors: %s\nTotal errors: %s' % (idc_prefix, err_0))

            arch_errors.append('%s archiver: Total errors: %s' % (idc_prefix, err_0))
            arch_errors.append('Log location: %s' % url_fname)
            arch_errors.append('')
            create_footer(aname)

            sendmail = archiver_sendmail
            sendmail_messages = archiver_sendmail_messages
            log_file_errors = arch_errors
            archiver_errors[0] = archiver_errors_list
    if show_times == True:
        print '%s Finished archiverlogs job in %s' % ( idc_prefix, (datetime.datetime.now()-archiver_logs_time))


def database_logs(sendmail, sendmail_messages, log_file_errors, idc_prefix, database_url, idc_link, i, current_date, current_time, database_errors):
    #print 'Starting database logs for ', idc_prefix
    database_logs_time = datetime.datetime.now()
    db_logs_sendmail = sendmail
    db_logs_sendmail_messages = sendmail_messages
    db_logs_errors = log_file_errors
    database_errors_list = database_errors[0]

    basic_auth(sendmail, sendmail_messages, log_file_errors, database_url, idc_prefix)

    err_0 = 0
    err_1 = 0

    if parse_output:
        if parse_output.find(current_date) == -1:
            db_logs_errors.append('%s database: No database log file found' % idc_prefix)
            db_logs_errors.append('')
        else:
            dname = 'D:/apache2/Apache2/htdocs/' + idc_prefix + '/database_' + current_date + '.html'
            url_fname = ip_address + "/" + idc_prefix + "/database_" + current_date + ".html"

            if os.path.isfile(dname):
                os.remove(dname)

            data_file = open(dname, 'ab')
            create_header(dname, current_date, current_time)
            log_counter = 0

            for each_log_line in parse_output.splitlines(True):
                if log_counter == 0:
                    log_url = BeautifulSoup(each_log_line)
                    my_regex = r"" + re.escape(current_date)

                    if re.search(my_regex, each_log_line, re.IGNORECASE):
                        log_counter = 1

                        for ahref in log_url.findAll('a', href=True):
                            log_link = ahref['href']
                            log_url = "http://" + idc_link + "/idc/groups/secure/logs/database/" + log_link
                            basic_auth(sendmail, sendmail_messages, log_file_errors, log_url, idc_prefix)

                            for line_in_log in parse_output.splitlines(True):
                                ldap_soup = BeautifulSoup(line_in_log)

                                for error_loop in ldap_soup.findAll('tr'):
                                    error_type = error_loop.contents[0].text
                                    error_date = error_loop.contents[1].text
                                    error_data = ''.join(split(error_loop.contents[2].text, 240)).replace("[ Details ]", "")

                                    if "skip_this_data_error" in error_data:
                                        err_1 += 1
                                        continue
                                    else:
                                        err_0 += 1
                                        s = u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (error_type, error_date, error_data)
                                        encoded_text = s.encode('ascii', 'ignore')
                                        data_file.write("\n" + encoded_text)
                else:
                    break

            data_file.close()

            if err_1 != 0:
                db_logs_errors.append("%s skip_this_data_error: %s" % (idc_prefix, err_1))

            if err_0 > 1:
                if len(database_errors_list[i]) == 0:
                    database_errors_list[i].append(err_0)
                    db_logs_sendmail.value = True
                    #print 'archiver_sendmail'
                    db_logs_sendmail_messages.append('Found database errors: %s\nTotal errors: %s' % (idc_prefix, err_0))
                elif len(database_errors_list[i]) >= 1:
                    if err_0 > int(database_errors_list[i][int(len(database_errors_list[i]) - 1)]):
                        database_errors_list[i].append(err_0)
                        db_logs_sendmail.value = True
                        #print 'archiver_sendmail'
                        db_logs_sendmail_messages.append('Found database errors: %s\nTotal errors: %s' % (idc_prefix, err_0))


            db_logs_errors.append('%s database: Other errors: %s' % (idc_prefix, err_0))
            db_logs_errors.append('%s database: Total errors: %s' % (idc_prefix, (int(err_0) + int(err_1))))
            db_logs_errors.append('Log location: %s' % url_fname)
            db_logs_errors.append('')
            create_footer(dname)

        sendmail = db_logs_sendmail
        sendmail_messages = db_logs_sendmail_messages
        log_file_errors = db_logs_errors
        database_errors[0] = database_errors_list

    else:
        db_logs_errors.append('%s: No data to read from parse_output: %s' % (idc_prefix, database_url))

    if show_times == True:
        print '%s Finished databaselogs job in %s' % (idc_prefix, (datetime.datetime.now()-database_logs_time))


def parse_balancer(sendmail, sendmail_messages, log_file_errors, idc_prefix, balancers):
    #pass
    #print 'Start asda'
    parse_balancer_time = datetime.datetime.now()
    balancer_logs_sendmail = sendmail
    balancer_logs_sendmail_messages = sendmail_messages
    balancer_logs_errors = log_file_errors

    if idc_prefix == 'contrib' or idc_prefix == 'intra' or idc_prefix == 'cons':
        for each_balancer in balancers:
            #print 'parsing balancer:', each_balancer
            f5_url = 'http://balancer.net/cgi-bin/balance.cgi?param1=' + each_balancer
            basic_auth(sendmail, sendmail_messages, log_file_errors, f5_url, idc_prefix)

            if parse_output:
                for f5_line in parse_output.splitlines(True):
                    #print f5_line
                    ldap_soup = BeautifulSoup(f5_line)
                    for f5_results in ldap_soup.findAll('td'):
                        f5_red_node = f5_results.find('font', color='RED')
                        f5_node_ip = f5_results.find('i')
                        if f5_red_node:
                            #skip this nodes....they are always down
                            if str(f5_node_ip.contents[0]) == 'IP: skip this ip' or \
                                str(f5_node_ip.contents[0]) == 'IP: skip this ip' or \
                                str(f5_node_ip.contents[0]) == 'IP: skip this ip' or \
                                str(f5_node_ip.contents[0]) == 'IP: skip this ip':
                                pass
                            else:
                                balancer_logs_sendmail.value = True
                                balancer_logs_sendmail_messages.append('%s: node name: %s\nnode ip: %s ' % (f5_url, f5_red_node.contents[0], f5_node_ip.contents[0]))
                                balancer_logs_errors.append('%s: node name: %s\nnode ip: %s ' % (f5_url, f5_red_node.contents[0], f5_node_ip.contents[0]))

            sendmail = balancer_logs_sendmail
            sendmail_messages = balancer_logs_sendmail_messages
            log_file_errors = balancer_logs_errors

    if show_times == True:
        print '%s Finished parsebalancer job in %s' % (idc_prefix, (datetime.datetime.now()-parse_balancer_time))

def check_robot(sendmail, sendmail_messages, log_file_errors, robot_time_from):

    check_robot_sendmail = sendmail
    check_robot_sendmail_messages = sendmail_messages
    check_robot_log_file_errors = log_file_errors


    robot_ids = ['robot_1', 'robot_2']

    for robot_id in robot_ids:
        url = 'https://link.to.robot/robots/getRobot.php?id=' + robot_id + '&from=' + robot_time_from + '&till=6&limit=15&only_errors=on'
        basic_auth(sendmail, sendmail_messages, log_file_errors, url)

        if parse_output:
            if "background-color: red" in parse_output:
                print '%s is down' % robot_id
        else:
            print "Robot %s - no result for: %s" % (robot_id, url)

    sendmail = check_robot_sendmail
    sendmail_messages = check_robot_sendmail_messages
    log_file_errors = check_robot_log_file_errors


#List to hold information if a new day is changed
days = []
#List to declare empty arrays only once
lists_done = []

if __name__ == '__main__':
    if debug:
        print '[%s] name is main - start script' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #Script must work in infinite loop even if exception occurs
    while True:
        try:
            while True:
                script_start = datetime.datetime.now()
                d = datetime.datetime.now() - datetime.timedelta(hours=1)
                dRobot = datetime.datetime.now() - datetime.timedelta(minutes=5)

                current_date = d.strftime("%Y-%m-%d")
                current_date_dRobot = dRobot.strftime("%Y-%m-%d")
                current_time = d.strftime("%H:%M:%S")
                current_time_dRobot = dRobot.strftime("%H:%M:%S")

                current_date_time = d.strftime("%Y-%m-%d %H:%M:%S")

                current_date_time_for_robot = "%s+%s" % (current_date_dRobot, current_time_dRobot)
                robot_time_from = current_date_time_for_robot#.replace(":", "%3A")

                current_day = d.strftime("%d")
                day_of_the_week = int(datetime.datetime.today().weekday())
                current_time_hours = int(d.strftime("%H"))

                #dynamic sleeptime depending on day of the week/time.
                #While at work, run script every 2 minutes
                #When not at work, run once in 30 minutes.
                #During weekends, run once per an hour

                if 0 <= day_of_the_week <= 4:
                    if debug:
                        print '[%s] day of the week is 0 is between 4: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), day_of_the_week)
                    if 7 <= current_time_hours <= 17:
                        if debug:
                            print '[%s] current time hours is between 7:00 and 1700: %s. Sleep time should be 120.' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), current_time_hours)
                        timesleep = 120
                    else:
                        if debug:
                            print '[%s] current time hours is between 17:00 and 7:00: %s. Sleep time should be 1800' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), current_time_hours)
                        timesleep = 1800
                else:
                    if debug:
                        print '[%s] day of the week is 4 is between 6: %s. Sleep time should be 3600.' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), day_of_the_week)
                    timesleep = 3600

                if debug:
                    print '[%s] Controlling sleep time: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), timesleep)

                #Manager to share objects between processes
                manager = Manager()
                #If False - dont send. If true - send email report
                sendmail = manager.Namespace()
                #By default don't send email
                sendmail.value = False
                #Errors array contains what we write into file
                log_file_errors = manager.list()
                #Sendmail_message array contains what we send to email
                sendmail_messages = manager.list()
                #Those arrays will be created on script start
                if len(lists_done) == 0:
                    if debug:
                        print '[%s] len lists_done is 0: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(lists_done))
                        print '[%s] Creating main arrays to hold data.' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    content_errors = manager.list()
                    archiver_errors = manager.list()
                    database_errors = manager.list()
                    archiver_errors.append([[], [], [], [], []])
                    database_errors.append([[], [], [], [], []])
                    #Yes. We need to add content_errors twice: [0] will hold , [1] will hold...
                    content_errors.append([[], [], [], [], []])
                    content_errors.append([[], [], [], [], []])
                    if debug:
                        print '[%s] Printing arrays...' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '[%s] SHOULD BE EMPTY content_errors: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ','.join(str(v) for v in content_errors))
                        print '[%s] SHOULD BE EMPTY archiver_errors: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ','.join(str(v) for v in archiver_errors))
                        print '[%s] SHOULD BE EMPTY: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ','.join(str(v) for v in database_errors))

                    lists_done.append(1)
                #i is an indexer for each environment (0,1,2,3,4)
                i = -1
                #Main report file for all errors. Also we send this file in email attachment if error occurs.
                email_report = 'D:/apache2/Apache2/htdocs/reports/report_' + current_date + '.txt'
                #Days list to track new day change
                if len(days) == 0:
                    if debug:
                        print '[%s] len days is 0: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(days))
                    days.append(current_day)

                #Reset all values on a day change
                if current_day != days[0]:
                    if debug:
                        print '[%s] len days is not 0: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(days))
                        print '[%s] the day in array and current day are different: %s vs %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), days[0], current_day)
                        print '[%s] Reseting all arrays...' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    days = []
                    content_errors = manager.list()
                    archiver_errors = manager.list()
                    database_errors = manager.list()
                    archiver_errors.append([[], [], [], [], []])
                    database_errors.append([[], [], [], [], []])
                    content_errors.append([[], [], [], [], []]) #this one will store the list of special errors
                    content_errors.append([[], [], [], [], []]) #this one will remember rows, where to start reading the content log file
                    if debug:
                        print '[%s] Printing current values for arrays...' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '[%s] SHOULD BE EMPTY days: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ', '.join(days))
                        print '[%s] SHOULD BE EMPTY content_errors: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ','.join(str(v) for v in content_errors))
                        print '[%s] SHOULD BE EMPTY archiver_errors: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ','.join(str(v) for v in archiver_errors))
                        print '[%s] SHOULD BE EMPTY database_errors: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ','.join(str(v) for v in database_errors))

                if debug:
                    print '[%s] Current content_errors: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ','.join(str(v) for v in content_errors))
                    print '[%s] Current archiver_errors: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ','.join(str(v) for v in archiver_errors))
                    print '[%s] Current database_errors: %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ','.join(str(v) for v in database_errors))

                log_file_errors.append("\n\n\n\n\n%s: Starting report..." % current_date_time)
                log_file_errors.append("-----------------------------------------------------------------------------------------------")

                for each_server in ucm_servers:
                    i += 1
                    idc_link = each_server[0]
                    idc_prefix = each_server[1]
                    db_ip = each_server[2]
                    db_port = each_server[3]
                    db_sid = each_server[4]
                    db_user = each_server[5]
                    db_pass = each_server[6]
                    nodes = each_server[7]
                    balancers = each_server[8]

                    if debug:
                        print '[%s] Getting information from ucm_servers array: ' \
                              '\ni = %s\n' \
                              'idc_link = %s\n' \
                              'idc_prefix = %s\n' \
                              'db_ip = %s\n' \
                              'db_port = %s\n' \
                              'db_sid = %s\n' \
                              'db_user = %s\n' \
                              'db_pass = %s\n' \
                              'nodes = %s\n' \
                              'balancers = %s' \
                              % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), i, idc_link, idc_prefix, db_ip, db_port, db_sid, db_user, db_pass, nodes, balancers)

                    if debug:
                        print '[%s] Current sendmail value (should be false): %s' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sendmail.value)
                        print '[%s] Launching processes... ' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    log_file_errors.append('Checking: %s' % idc_prefix)

                    content_url = "http://" + idc_link + "/idc/groups/secure/logs/IdcLnLog.htm"
                    archiver_url = "http://" + idc_link + "/idc/groups/secure/logs/archiver/ArchiveLn.htm"
                    database_url = "http://" + idc_link + "/idc/groups/secure/logs/database/DatabaseLn.htm"

                    contentlogs = multiprocessing.Process(name='contentlogs',
                                                          target=content_logs,
                                                          args=(sendmail, sendmail_messages, log_file_errors, idc_prefix, content_url, idc_link,
                                                                current_date, current_time, content_errors, i, ))
                    contentlogs.daemon = True

                    if debug:
                        print '[%s] Process 1: contentlogs' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '[%s] Process 1: passing the following params:' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '\tsendmail = %s\n' \
                              '\tsendmail_messages = %s\n' \
                              '\terrors = %s\n' \
                              '\tidc_prefix = %s\n' \
                              '\tcontent_url = %s\n' \
                              '\tidc_link = %s\n' \
                              '\tcurrent_date = %s\n' \
                              '\tcurrent_time = %s\n' \
                              '\tcontent_errors = %s\n' \
                              '\ti = %s' \
                              % (sendmail, sendmail_messages, log_file_errors, idc_prefix, content_url, idc_link, current_date, current_time, content_errors, i)

                    checkdb = multiprocessing.Process(name='checkdb',
                                                      target=check_db,
                                                      args=(sendmail, sendmail_messages, log_file_errors, idc_prefix, db_ip, db_port, db_sid,
                                                            db_user, db_pass, ))
                    checkdb.daemon = True

                    if debug:
                        print '[%s] Process 2: checkdb' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '[%s] Process 2: passing the following params:' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '\tsendmail = %s\n' \
                              '\tsendmail_messages = %s\n' \
                              '\terrors = %s\n' \
                              '\tidc_prefix = %s\n' \
                              '\tdb_ip = %s\n' \
                              '\tdb_port = %s\n' \
                              '\tdb_sid = %s\n' \
                              '\tdb_user = %s\n' \
                              '\tdb_pass = %s' \
                              % (sendmail, sendmail_messages, log_file_errors, idc_prefix, db_ip, db_port, db_sid, db_user, db_pass)

                    checknodes = multiprocessing.Process(name='checknodes',
                                                         target=check_nodes,
                                                         args=(sendmail, sendmail_messages, log_file_errors, idc_prefix, nodes, ))
                    checknodes.daemon = True

                    if debug:
                        print '[%s] Process 3: checknodes' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '[%s] Process 3: passing the following params:' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '\tsendmail = %s\n' \
                              '\tsendmail_messages = %s\n' \
                              '\terrors = %s\n' \
                              '\tidc_prefix = %s\n' \
                              '\tnodes = %s' \
                              % (sendmail, sendmail_messages, log_file_errors, idc_prefix, nodes)

                    parseproviders = multiprocessing.Process(name='parseproviders',
                                                             target=parse_providers,
                                                             args=(sendmail, sendmail_messages, log_file_errors, idc_prefix, idc_link, ))
                    parseproviders.daemon = True

                    if debug:
                        print '[%s] Process 4: parseproviders' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '[%s] Process 4: passing the following params:' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '\tsendmail = %s\n' \
                              '\tsendmail_messages = %s\n' \
                              '\terrors = %s\n' \
                              '\tidc_prefix = %s\n' \
                              '\tidc_link = %s' \
                              % (sendmail, sendmail_messages, log_file_errors, idc_prefix, idc_link)

                    archiverlogs = multiprocessing.Process(name='archiverlogs',
                                                           target=archiver_logs,
                                                           args=(sendmail, sendmail_messages, log_file_errors, idc_prefix, archiver_url, idc_link, i,
                                                                 current_date, current_time, archiver_errors, ))
                    archiverlogs.daemon = True

                    if debug:
                        print '[%s] Process 5: archiverlogs' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '[%s] Process 5: passing the following params:' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '\tsendmail = %s\n' \
                              '\tsendmail_messages = %s\n' \
                              '\terrors = %s\n' \
                              '\tidc_prefix = %s\n' \
                              '\tarchiver_url = %s' \
                              '\tidc_link = %s' \
                              '\ti = %s' \
                              '\tcurrent_date = %s' \
                              '\tcurrent_time = %s' \
                              '\tarchiver_errors = %s' \
                              % (sendmail, sendmail_messages, log_file_errors, idc_prefix, archiver_url, idc_link, i, current_date, current_time, archiver_errors)

                    databaselogs = multiprocessing.Process(name='databaselogs',
                                                           target=database_logs,
                                                          args=(sendmail, sendmail_messages, log_file_errors, idc_prefix, database_url, idc_link, i,
                                                                 current_date, current_time, database_errors, ))
                    databaselogs.daemon = True

                    if debug:
                        print '[%s] Process 6: databaselogs' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '[%s] Process 6: passing the following params:' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '\tsendmail = %s\n' \
                              '\tsendmail_messages = %s\n' \
                              '\terrors = %s\n' \
                              '\tidc_prefix = %s\n' \
                              '\tdatabase_url = %s' \
                              '\tidc_link = %s' \
                              '\ti = %s' \
                              '\tcurrent_date = %s' \
                              '\tcurrent_time = %s' \
                              '\tdatabase_errors = %s' \
                              % (sendmail, sendmail_messages, log_file_errors, idc_prefix, database_url, idc_link, i, current_date, current_time, database_errors)

                    parsebalancer = multiprocessing.Process(name='databaselogs',
                                                            target=parse_balancer,
                                                            args=(sendmail, sendmail_messages, log_file_errors, idc_prefix, balancers, ))
                    parsebalancer.daemon = True

                    if debug:
                        print '[%s] Process 7: parsebalancer' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '[%s] Process 7: passing the following params:' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print '\tsendmail = %s\n' \
                              '\tsendmail_messages = %s\n' \
                              '\tlog_file_errors = %s\n' \
                              '\tidc_prefix = %s\n' \
                              '\tbalancers = %s' \
                              % (sendmail, sendmail_messages, log_file_errors, idc_prefix, balancers)

                    #Start all functions at once
                    contentlogs.start()
                    checkdb.start()
                    checknodes.start()
                    parseproviders.start()
                    archiverlogs.start()
                    databaselogs.start()
                    parsebalancer.start()

                    #print 'contentlogs.is_alive()', contentlogs.is_alive()

                    #Join them to wait until all functions are done
                    contentlogs.join()
                    checkdb.join()
                    checknodes.join()
                    parseproviders.join()
                    archiverlogs.join()
                    databaselogs.join()
                    parsebalancer.join()

                    #print 'contentlogs.is_alive()', contentlogs.is_alive()

                    log_file_errors.append("----------------------------------")
                    #break #for tests in dev env
                
                check_robot(sendmail, sendmail_messages, log_file_errors, robot_time_from)
                
                log_file_errors.append('Report finished in: %s' % (datetime.datetime.now()-script_start))
                log_file_errors.append("-----------------------------------------------------------------------------------------------")


                if os.path.isfile(email_report):
                    with open(email_report, "r") as myfile:
                        data = myfile.read()
                else:
                    data = ""

                print 'Send report:', sendmail.value
                print 'Completed in: ', (datetime.datetime.now()-script_start)
                print 'Sleeping for', timesleep


                if sendmail.value is True:
                    sendmail_out = '\n'.join(sendmail_messages)
                    send_mail('Found errors: \n%s' % sendmail_out, email_report, log_file_errors)
                else:
                    open_file = open(email_report, 'w')
                    message = '\n'.join(log_file_errors)
                    open_file.write('\n%s\n%s' % (message, data))
                    open_file.close()

                time.sleep(timesleep)


        except Exception, err:

            print traceback.format_exc()
            time.sleep(600)
