import sys
import json
import warnings
import logging
import time
import uuid
import requests

if sys.version > '3':
    from urllib.parse import urljoin
else:
    from urlparse import urljoin

class RPCError(Exception):
    def __init__(self, code, message):
        super(RPCError, self).__init__('{} {}'.format(code, message))
        self.code = code
        self.message = message

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
            except requests.exceptions.ConnectionError as e:
                if i >= retry - 1:
                    raise
                logging.debug('conn error: %s', e)
                time.sleep(0.1)

    def _request(self, srv, method, *params):
        url = urljoin(self.connect,
                      '/jsonrpc/2.0/api')

        method = srv + '::' + method
        payload = {
            'id': uuid.uuid4().hex,
            'method': method,
            'params': params
            }
        resp = self.session.post(url, json=payload, timeout=10)
        try:
            response = resp.json()
        except json.decoder.JSONDecodeError:
            raise RPCError(resp.status_code, resp.text)

        if response.get('error'):
            logging.warn('walltfarm error response: %s',
                         response['error'])
            raise RPCError(response['error'].get('code'),
                           response['error'].get('message'))
        return response

    def __del__(self):
        self.session = None

