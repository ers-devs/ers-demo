#!/usr/bin/env python

import json, time, random
from twisted.internet import reactor
from twisted.web import proxy, http
from ers import ERSLocal

import ipdb

def header2json(header):
    [f for f in header.getAllRawHeaders()]

def json2header(json_string):
    pass

class CommonProxyClient(proxy.ProxyClient):
    def handleHeader(self, key, value):
        proxy.ProxyClient.handleHeader(self, key, value)

    def handleResponsePart(self, buffer):
        # ipdb.set_trace()
        """
        if self.father.is_cacheable():
            # print "caching"
            cache.add_data(self.father.request_id, 'http:content', buffer, provenance)
            headers_string = json.dumps(tuple(self.father.responseHeaders.getAllRawHeaders()))
            cache.add_data(self.father.request_id, 'http:responseHeaders',
                headers_string, provenance)
        #else:
        #   print "will not cache"

        """
        proxy.ProxyClient.handleResponsePart(self, buffer)

class CommonProxyClientFactory(proxy.ProxyClientFactory):
    protocol = CommonProxyClient

class CommonProxyRequest(proxy.ProxyRequest):
    protocols = {'http': CommonProxyClientFactory}

    def process(self):
        self.log_request()
        try:
            proxy.ProxyRequest.process(self)
        except KeyError:
            print "HTTPS is not supported at the moment!"

    def log_request(self):
        call_time = time.time()
        self.request_id = 'urn:http:request:{0}{1}'.format(call_time, random.randint(1000,9999))
        headers = self.getAllHeaders()
        cache.add_data(self.request_id, 'http:url', self.uri, provenance)
        cache.add_data(self.request_id, 'dct:date', time.asctime(time.gmtime(call_time)), provenance)
        cache.add_data(self.request_id, 'http:headers', json.dumps(headers), provenance)
        cache.add_data(self.request_id, 'http:mthd', self.method, provenance)

    def is_cacheable(self):
        """
        Response is cacheable if 'text' occurs in headers['content-type'] and
        headers['content-length'] < 100000
        """
        try:
            length = int(self.responseHeaders.getRawHeaders('content-length')[0])
            is_text = any([t.find('text') >=0 for t in self.responseHeaders.getRawHeaders('content-type')])
        except TypeError:
            return False
        return self.code==200 and is_text and length < 10e5

class CommonProxy(proxy.Proxy):
    requestFactory = CommonProxyRequest

class CommonProxyFactory(http.HTTPFactory):
    def buildProtocol(self, addr):
        return CommonProxy()

provenance = 'local'
cache = ERSLocal(dbname='cache')

reactor.listenTCP(8080, CommonProxyFactory())
reactor.run()
