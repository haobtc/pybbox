import sys
import json
import warnings
import logging
import time
import requests

logger = logging.getLogger(__name__)

if sys.version > '3':
    from urllib.parse import urljoin
else:
    from urlparse import urljoin

class RPCError(Exception):
    def __init__(self, code, message):
        super(RPCError, self).__init__('{} {}'.format(code, message))
        self.code = code
        self.message = message

class HTTPError(Exception):
    def __init__(self, code, message):
        super(HTTPError, self).__init__('{} {}'.format(code, message))
        self.code = code
        self.message = message

request_id_counter = 0
def next_request_id():
    global request_id_counter
    request_id_counter += 1
    return request_id_counter

class BBoxClient(object):
    def __init__(self, connect, cert=None):
        self.connect = connect
        self.session = requests.session()
        if cert is not None:
            assert connect.startswith('https:')
            self.session.verify = cert

    def request_result(self, srv, method, *params, **kw):
        return self.request(srv, method, *params, **kw)['result']

    def request(self, srv, method, *params, **kw):
        retry = kw.pop('retry', 1)
        assert retry >= 1
        for i in range(retry):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    return self._request(srv, method, *params)
            except (requests.exceptions.ConnectionError, HTTPError):
                if i >= retry - 1:
                    raise
                logger.warn('conn error while requesting %s::%s', srv, method, exc_info=True)
                time.sleep(1.0)


    def _request(self, srv, method, *params):
        url = urljoin(self.connect,
                      '/jsonrpc/2.0/api')

        method = srv + '::' + method
        payload = {
            'id': next_request_id(),
            'method': method,
            'params': params
            }
        resp = self.session.post(url, json=payload, verify=False, timeout=10)
        if resp.status_code >= 300 or resp.status_code < 200:
            # status 2xx is considered right response
            raise HTTPError(resp.status_code, resp.text)

        try:
            response = resp.json()
        except json.decoder.JSONDecodeError:
            raise HTTPError(resp.status_code, resp.text)

        if response.get('error'):
            logger.warn('walltfarm error response: %s',
                        response['error'])
            raise RPCError(response['error'].get('code'),
                           response['error'].get('message'))
        return response

    def __del__(self):
        self.session = None

