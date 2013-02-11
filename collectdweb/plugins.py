#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import hashlib
import hmac

import bottle

from collectdweb.models import DoesNotExist
from collectdweb.patterns import Filters

class Detect404(object):
    api = 2
    name = 'detect_404'

    def apply(self, callback, route):
        def inner_detect_404(**kw):
            try:
                return callback( **kw)
            except DoesNotExist, e:
                raise bottle.HTTPError( 404, str(e))
        return inner_detect_404

class FakeModel(object):
    def __init__(self, grouper, model, full_name):
        self.model = model
        self.full_name = full_name
        if grouper and self.full_name != model.full_name:
            self.full_name += grouper + '*'

    def __getattr__(self, name):
        return getattr(self.model, name)

class GroupBy(object):
    api = 2
    name = 'group_by'

    def __init__( self, ignored_groupers=None):
        self.ignored_groupers = frozenset( ignored_groupers) if ignored_groupers else frozenset()

    def apply(self, callback, route):
        def inner_group_by(**kw):
            all_the_results = callback( **kw)
            grouper = bottle.request.GET.get('group')
            if not grouper:
                return all_the_results
            groups = dict( ( model.full_name.split( grouper, 1)[0], model)
                for model in all_the_results)
            grouper = grouper if grouper not in self.ignored_groupers else None
            return [ FakeModel(grouper,host,name) for name,host in groups.items() ]
        return inner_group_by


class FilterObjectList(object):
    api = 2
    name = 'filter_list'

    def apply(self, callback, route):
        def inner_filter_list(**kw):
            all_the_results = callback( **kw)
            filter = Filters( bottle.request.GET.getall('pattern'))
            return [ x for x in all_the_results if filter.match( x.full_name)]
        return inner_filter_list

class Urlizer(object):
    api = 2
    name = 'urlizer'

    def __init__(self, pattern):
        self.pattern = pattern

    def apply(self, callback, route):
        def inner_urlize(**kw):
            all_the_results = callback( **kw)
            all_the_urls =  [ self.pattern.format( r) for r in all_the_results ]
            all_the_urls.sort()
            return all_the_urls
        return inner_urlize

class Signature(object):
    api = 2
    name = 'signature'

    def __init__(self, key):
        self.key = key

    def sign(self, path):
        return hmac.new( self.key, path, hashlib.sha1).hexdigest()

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

