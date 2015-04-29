import requests
import kerberos_sspi as kerberos
from requests.auth import HTTPBasicAuth

class KerberosTicket:
    def __init__(self, service):
        __, krb_context = kerberos.authGSSClientInit(service)
        try:
            kerberos.authGSSClientStep(krb_context, "")
        except Exception as ex:
            error = '{0}'.format(ex)
            print error
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

def basic_auth(url, idc_prefix=None):
    global parse_output

    #Use your OpenSSO link below
    krb = KerberosTicket("HTTP@opensso.YOURHOST.SOMETHING")
    headers = {"Authorization": krb.auth_header}
    #Define your basic auth stuff
    auth = HTTPBasicAuth('basic_user', 'basic_password')

    try:
        #Use kerberos first
        r = requests.get(url, headers=headers, timeout=20)

        #if kerberos fails, use basic auth
        if "Page not found" in r.content or "Authorization not granted" in r.content:
            r = requests.get(url, auth=auth, timeout=20)

        if "Authentication failed" in r.content:
            print 'Probably wrong HTTPBasicAuth credentials'

    except requests.exceptions.Timeout:
        print 'Timeout error for URL: %s' % url
    except Exception:
        print 'Bad URL: %s' % url
    else:
        parse_output = r.content
        return parse_output
