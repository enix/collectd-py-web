#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import hashlib
import hmac

import bottle

KEY = 'OP IS A FAG'


class Signature(object):
    api = 2
    name = 'signature'

    def sign(self, path):
        return hmac.new(KEY, path, hashlib.sha1).hexdigest()

    def reject(self, reason):
        raise bottle.HTTPError(403, reason)

    def apply(self, callback, route):
        def inner_signature(**kw):
            sign_ = bottle.request.GET['sign']
            if not sign_:
                return self.reject('Missing signature')

            path= bottle.request.environ['PATH_INFO']
            if sign_ != self.sign(path):
                return self.reject('Bad signature. You bastards!')

            return callback( **kw)
        return inner_signature

class DumpInJSON( object):
    api = 2
    name='dump_json'
    def apply(self, callback, route):
        def inner( **kw):
            result = callback( **kw)
            if ( result is None or
                    isinstance( result, bottle.HTTPResponse) or
                    result is bottle.response
                    ):
                return result
            bottle.response.set_header( 'content_type', 'application/json')
            return json.dumps( result)
        return inner

