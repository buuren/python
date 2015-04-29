import re

find_ucmid_in_xml = re.compile(
    r'(?:.*?://)?([^/\r\n]+)(/[^\r\n]*)?'
)

urls = [
    'http://www.google.1?asdasd.asdasd',
    'ftp://www.google.2/ftp',
    'sftp://www.google.3/sftp',
    'https://www.goo:Dgle.4',
    'http://test.google.5',
    'https://_asdas-dSAd-asdasvladimir.6',
    'a.vam.7/url',
    'trans.vam.7/url',
    'www.noprot.8/www',
    'http://www.hello-world.9/test',
    'http://www.example.10/artom_loh/asdasda',
    'http://stackoverflow.com/questions/tagged/regex',
    'http://ee.123.net/index.htm#&panel1-1'
]

for each_url in urls:
    siteid_in_project_file = re.search(find_ucmid_in_xml, each_url)
    if siteid_in_project_file:
        print siteid_in_project_file.group(1)
        print '========================================'
