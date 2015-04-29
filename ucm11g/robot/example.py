#!/usr/local/bin/python2.7

__author__ = 'stuart robinson'
from ucm11g import UcmClient, ServiceFailed
from BeautifulSoup import BeautifulSoup
import sys

ucmClient = UcmClient('your.host.goes', '80')
ucmClient.login('user', 'pass')

url = 'http://your_url.com/something'

def parse_providers(url):

    parse_output = ucmClient.open_url(url)

    if parse_output:
        output_soup = BeautifulSoup(parse_output)
        table = output_soup.findAll("table", {"id": "table_0"})

        if table:
            for each_tr in table:
                rows = each_tr.findAll("tr")
                for row in rows:
                    tds = row.findAll("td")
                    provider_name = tds[0].text.strip('\n').strip()
                    provider_state = tds[6].text.strip('\n').strip()

                    for each_word in provider_state.split():
                        if 'down' in each_word:
                            print 'is down', provider_name
                    for each_word in provider_state.split():
                        if each_word is '0':
                            print 'is 0', provider_name

parse_providers(url)

sys.exit(1)
#Search for files of type News

ucmServiceData = {
        'QueryText': 'dDocType<matches>`Document`',
        'ResultCount': 10
}


try:
        search = ucmClient.call_service('GET_SEARCH_RESULTS', ucmServiceData)
        #Access resultset by name and iterate through results
        for doc in search.fetch('SearchResults'):
                print doc['dDocName']

except ServiceFailed as e:
        print 'search failed - %s' % e




#build a dictionary of service parameters.
ucmServiceData = {
        'dDocTitle': 'New Article 1',
        'dDocName': 'News_Article_01',
        'dDocType': 'News',
        'dDocAuthor': 'weblogic',
        'dDocAccount': 'weblogic',
        'dSecurityGroup': 'Public',
        #files can be submitted using an open file object
        'primaryFile': open('news.txt', 'r')
}

try:
        ucmClient.call_service('CHECKIN_UNIVERSAL', ucmServiceData)
except ServiceFailed as e:
        print 'checkin failed - %s' % e
