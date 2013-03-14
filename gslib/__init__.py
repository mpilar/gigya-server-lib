# -*- coding: utf-8 -*-
"""
gslib
~~~~~

:copyright: (c) 2012 by Miguel Pilar.
:license: MIT, see LICENSE.txt for more details.

"""

__title__ = 'gslib'
__version__ = "0.1.4"
__author__ = 'Miguel Pilar'
__license__ = 'MIT'
__copyright__ = 'Copyright 2012 Miguel Pilar'


import hmac
import binascii
import sys
from time import time
from hashlib import sha1
from base64 import b64decode

import requests


API_KEY = None
SECRET_KEY = None
# Try to import settings from django or flask
try:
    from django.conf import settings
    if hasattr(settings, "GIGYA_API_KEY"):
        API_KEY = settings.GIGYA_API_KEY
    if hasattr(settings, "GIGYA_SECRET_KEY"):
        SECRET_KEY = settings.GIGYA_SECRET_KEY
except ImportError:
    pass


class GSException (Exception):
    pass


class GSConnectionException (GSException):
    pass


__FLASK_APP__ = None


def initialize_app(app=None):
    """
    Use to initialize gslib with a flask app's configuration.
    """
    if app is not None:
        global __FLASK_APP__
        __FLASK_APP__ = app
        app.config.setdefault('GIGYA_API_KEY', None)
        app.config.setdefault('GIGYA_SECRET_KEY', None)


class Request (object):
    """
    Represents a request to the Gigya Socialize API.
    Sample usage:
        response = gslib.Request('gcs.getUserData',
                    params={'UID': '<user UID>', 'fields': '*'},
                    use_https=True).send()
    The Request object behaves like a dict containing the parameters, so the
    following code is also valid (and does the same as above):
        request = gslib.Request('gcs.getUserData', use_https=True)
        request['UID'] = '<user UID>'
        request['fields'] = '*'
        response = request.send()

    It's important to note that send() will convert a json response into a
    native representation automatically, xml responses are returned as text.
    """
    params = {}

    def __init__(self, api_method, api_key=API_KEY,
            secret_key=SECRET_KEY, params={}, use_https=False):
        """
        Build a request.
        """
        if not api_method:
            raise GSException("No API method specified.")

        if __FLASK_APP__:
            if not api_key:
                api_key = __FLASK_APP__.config["GIGYA_API_KEY"]
            if not secret_key:
                secret_key = __FLASK_APP__.config["GIGYA_SECRET_KEY"]

        if api_method[0] == "/":
            api_method = api_method[1:]

        if api_method.rfind(".") == 0:
            self.domain = "socialize.gigya.com"
            self.path = "/" + api_method
        else:
            tokens = api_method.split(".")
            self.domain = tokens[0] + ".gigya.com"
            self.path = "/" + api_method

        self.method = api_method

        if params:
            self.params = params

        self.domain = self.params.get("_host", self.domain)

        self.use_https = use_https
        self.api_key = api_key
        self.secret_key = secret_key

    def __getitem__(self, key):
        return self.params[key]

    def __setitem__(self, key, value):
        self.params[key] = value

    def __len__(self):
        return len(self.params)

    def clear(self):
        """
        Clears any parameters set.

        Important: does not clear any settings configured in the constructor.
        """
        self.params = {}

    def send(self, timeout=None, force_text_response=False):
        """
        Perform the request.
        It's important to note that a json response is converted into a native
        representation automatically, xml responses are returned as text.
        """
        if "format" not in self.params:
            self.params["format"] = "json"

        if (not (self.api_key and self.method)) or \
                (not (self.secret_key or self.token)):
            raise GSConnectionException("Required parameter is missing")

        try:
            self["httpStatusCodes"] = False
            response = Request.send_request(
                        "POST", self.domain, self.path,
                        self.params, self.api_key, self.secret_key,
                        self.use_https, timeout)
            if self.params["format"] == "xml" or force_text_response:
                return response.text
            if self.params["format"] == "json":
                return response.json()

        except Exception as ex:
            raise  GSConnectionException(str(ex)), None, \
                                            sys.exc_info()[2]

    @classmethod
    def send_request(cls, method, domain, path, params, token, secret,
            use_https, timeout=None):
        """
        Performs a Gigya REST request.
        """
        params["sdk"] = "python" + __version__

        scheme = "https" if (use_https or not secret) else "http"
        port = 443 if scheme[-1] == "s" else 80
        host = domain
        if ":" in domain:
            _ds = domain.split(":")
            port = int(_ds[-1])
            host = ":".join(_ds[:-1])
        resource_uri = "{scheme}://{domain}{path}".format(scheme=scheme,
                                            domain=domain.lower(), path=path)

        nonce = int(time() * 1000)
        timestamp = str(nonce / 1000)
        nonce = str(nonce)

        http_method = method

        if secret:
            params["apiKey"] = token
            if use_https:
                params["secret"] = secret
            else:
                params["timestamp"] = timestamp
                params["nonce"] = nonce

                signature = cls.oauth_signature(
                                secret, http_method, scheme, host, port,
                                path, params)
                params["sig"] = signature
        else:
            params["oauth_token"] = token

        req = requests.request(method, resource_uri, data=params, timeout=timeout)
        return req

    @classmethod
    def oauth_signature(cls, hmac_key, method, scheme, host, port, path,
            request_params):
        """
        Calculates an oauth signature
        """
        normalized_url = "{scheme}://{host}".format(scheme=scheme, host=host)
        if not (port and ((int(port) == 80 and scheme == "http") or
                          (int(port) == 443 and scheme == "https"))):
            normalized_url = normalized_url + str(port)

        normalized_url = normalized_url + path
        qs_params = []
        for key in sorted(request_params.keys()):
            value = request_params.get(key, "")
            if value is None:
                value = ""
            qs_params.append("=".join([key, str(value)]))

        query_string = "&".join(qs_params)

        base_string = "&".join([method.upper(),
                               cls.oauth_urlencode(normalized_url),
                               cls.oauth_urlencode(query_string)])
        hashed = hmac.new(b64decode(hmac_key), base_string, sha1)
        return binascii.b2a_base64(hashed.digest())[:-1]

    @classmethod
    def oauth_urlencode(cls, url):
        return requests.utils.quote(url, safe="~")


class SigUtils():
    @classmethod
    def signature_validate(cls, timestamp, UID, signature, friendUID=None, secretKey=None):
        """
        Validate a Gigya message signature.
        See: http://bit.ly/NZ2Bpc
        """
        try:
            if not (signature and timestamp):
                return False
            if abs(time() - int(timestamp)) > 180:
                return False

            if not secretKey:
                if __FLASK_APP__:
                    secretKey = __FLASK_APP__.config["GIGYA_SECRET_KEY"]
                elif SECRET_KEY:
                    secretKey = SECRET_KEY

            if not secretKey:
                return False

            return cls._constant_time_compare(signature,
                cls.build_signature(secretKey, UID, timestamp, friendUID))

        except (TypeError, ValueError):
            return False

    @classmethod
    def _constant_time_compare(cls, a, b):
        """
        Constant-enough time compare, for comparing signatures and other
        hashes, do not use to compare plain text passwords (which shouldn't be
        happening anyways).
        """
        if len(a) != len(b):
            return False
        result = 0
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
        return result == 0

    @classmethod
    def build_signature(cls, key, UID, timestamp, friendUID=None):
        """
        Builds a gigya verification signature.
        """
        if not friendUID:
            base_string = str(int(timestamp)) + "_" + UID
        else:
            base_string = str(int(timestamp)) + "_" + friendUID + "_" + UID
        hashed = hmac.new(b64decode(key), base_string, sha1)
        return binascii.b2a_base64(hashed.digest())[:-1]


if __name__ == '__main__':
    from optparse import OptionParser
    try:
        import simplejson as json
    except ImportError:
        import json

    parser = OptionParser()
    parser.add_option("-a", "--api-key", dest="api_key",
            help="the Gigya API_KEY", metavar="API_KEY",
            default="2_6cIPnqrOU75VMqiYxer_n375YjH9JSu" \
                      "CFEo55XZAoUFaOBgdI11Qw8JerKOxjBbg")
    parser.add_option("-s", "--secret-key",
            action="store", dest="secret_key",
            help="the Gigya Secret Key")
    parser.add_option("-m", "--method", default="reports.getSocializeStats",
            action="store", dest="method", metavar="METHOD",
            help="the Gigya method to call ex. METHOD")
    parser.add_option("-p", "--params",
            action="store", dest="params",
            default='{"startDate": "08-09-2012", "endDate": "08-10-2012",'\
               '"dimensions": "cid,gender", "measures": "logins,referrals"}',
            help="the parameters to send to the gigya call in JSON format")
    parser.add_option("-n", "--no-ssl",
            action="store_false", dest="use_ssl",
            default=True,
            help="Disable using ssl/tls.")

    (options, args) = parser.parse_args()

    if not options.secret_key:
        print "No secret key provided, aborting"
        sys.exit(2)

    api_key = options.api_key
    secret = options.secret_key

    method = options.method
    payload = json.loads(options.params)
    request = Request(method, api_key, secret, params=payload,
                                  use_https=True)

    print request.send()
