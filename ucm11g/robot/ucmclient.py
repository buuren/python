__author__ = 'stuart robinson'

#!/usr/local/bin/python2.7
import cookielib
import urllib2
import MultipartPostHandler
import simplejson as json
import logging

logging.basicConfig()
log = logging.getLogger('ucmclient')

class UcmAuthHandler(urllib2.BaseHandler):
    def __init__(self, username, password, loginUrl, customHeaders=None):

        self.username = username
        self.password = password
        self.headers = customHeaders
        self.attempts = 0
        self.loginUrl = loginUrl

    def http_request(self, request):

        for header, value in self.headers.items():
            request.add_header(header, value)

        return request

    def http_response(self, request, response):

        code, msg, hdrs = response.code, response.msg, response.info()

        if code == 302 and '/adfAuthentication?login=true' in response.headers['location'] and self.attempts == 0:
            self.attempts = 1
            loginparmams = {
                'j_character_encoding': 'UTF-8',
                'j_username': self.username,
                'j_password': self.password,
            }
            urllib2.urlopen(self.loginUrl, loginparmams)
            response = urllib2.urlopen(urllib2.unquote(response.url))

        return response


    https_response = http_response


class ServiceResult(object):
    def __init__(self, results):
        self.results = results

    def fetch(self, resultset):
        fields = [field['name'] for field in self.results['ResultSets'][resultset]['fields']]

        return (dict(zip(fields, r)) for r in self.results['ResultSets'][resultset]['rows'])

    def status_code(self):
        return self.results.respObj['LocalData']['StatusCode']

    def status_message(self):
        return self.results.respObj['LocalData']['StatusMessage']


class ServiceFailed(Exception):
    def __init__(self, value, *args, **kwargs):
        self.value = value
        super(Exception, self).__init__(self, *args, **kwargs)

    def __str__(self):
        return repr(self.value)


class UcmClient(object):
    def __init__(self, host, port):

        self.csBaseUrl = 'http://%(host)s:%(port)s/cs' % {'host': host, 'port': port}
        self.idcUrl = ('%s/idcplg') % self.csBaseUrl
        self.host = host
        self.port = port
        self.idctoken = None

    def login(self, username, password):

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1b4) Gecko/20090427 Fedora/3.5-0.20.beta4.fc11 Firefox/3.5b4",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        cjar = cookielib.CookieJar()

        loginUrl = ('%s/login/j_security_check') % self.csBaseUrl

        opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(cjar),
            MultipartPostHandler.MultipartPostHandler,
            UcmAuthHandler(username, password, loginUrl, headers)
        )

        urllib2.install_opener(opener)

        log.info('Authenticating to UCM..')
        pingResp = self.call_service('PING_SERVER')
        self.idctoken = pingResp.results['LocalData']['idcToken']

        log.info('Authenticated')

    def open_url(self, url):
        response = urllib2.urlopen(url)
        return response.read()

    def call_service(self, serviceName, dataDict=None):

        if dataDict and self.idctoken:
            dataDict.update({'idcToken': self.idctoken})

        resp = urllib2.urlopen('%s?IdcService=%s&IsJson=1' % (self.idcUrl, serviceName), dataDict)
        respObj = json.loads(resp.read())

        if respObj['LocalData'].get('StatusCode', '0') != '0':
            raise ServiceFailed(respObj['LocalData']['StatusMessage'])
        elif 'StatusMessage' in respObj['LocalData']:
            log.info(respObj['LocalData']['StatusMessage'])

        return ServiceResult(respObj)
