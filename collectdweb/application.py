#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import bottle

from .models import Host, Plugin, Graph

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

dump_json =  DumpInJSON()

@bottle.route('/hosts/', apply=dump_json)
def list_hosts():
    return Host.objects.names()


@bottle.route('/hosts/<host_name>/', apply=dump_json)
def list_plugins( host_name):
    try:
        return list( set( x.name
            for x in Host.objects.get( host_name).plugins.all() ))
    except Host.DoesNotExist:
        raise bottle.HTTPError( 404, 'Host %s does not exist' % host_name)

@bottle.route('/hosts/<host_name>/<plugin_name>/', apply=dump_json)
def list_graphs( host_name, plugin_name):
    try:
        plugins = [ plugin 
                for plugin in Host.objects.get( host_name).plugins.all()
                if plugin.name == plugin_name ]
    except Host.DoesNotExist:
        raise bottle.HTTPError( 404, 'Host %s does not exist' % host_name)
    except Plugin.DoesNotExist:
        raise bottle.HTTPError( 404, 'Plugin %s does not exist' % plugin_name)

    plugins.sort( key=lambda x:x.instance)
    graphes = []
    for plugin in plugins:
        graphes.extend( plugin.graphes.all() )

    return [ get_url( graph) for graph in graphes ]

def get_url( graph):
    return '/hosts/{host}/{plugin}/{graph_name}.png'.format(
            host = graph.plugin.host.name,
            plugin = graph.plugin.full_name,
            graph_name = graph.full_name
            )


SUPPORTED_FORMATS = {
        'pdf': 'application:pdf',
        'eps': 'application/epd', 
        'svg': 'image/svg+xml',
        'png': 'image/png'
        }
@bottle.route('/hosts/<host_name>/<plugin_name>/<type>.png')
@bottle.route('/hosts/<host_name>/<plugin_name>/<type>-<type_instance>.png')
@bottle.route('/hosts/<host_name>/<plugin_name>-<plugin_instance>/<type>.png')
@bottle.route('/hosts/<host_name>/<plugin_name>-<plugin_instance>/<type>-<type_instance>.png')
def show_graph( host_name, plugin_name, type, plugin_instance=None, type_instance=None):
    try:
        graph = Host.objects.get( host_name
                ).plugins.get( plugin_name, plugin_instance
                ).graphes.get( type, type_instance)
    except Host.DoesNotExist:
        raise bottle.HTTPError( 404, 'Host %s does not exist' % host_name)
    except Plugin.DoesNotExist:
        raise bottle.HTTPError( 404, 'Plugin %s does not exist' % plugin_name)
    except Graph.DoesNotExist:
        raise bottle.HTTPError( 404, 'Graph %s does not exist' % plugin_instance)

    parameters = bottle.request.GET
    start, end = _resolve_timespan(
            parameters.get('timespan'),
            parameters.get('start'),
            parameters.get('end'))

    format = parameters.get('format','').lower()
    if not format in SUPPORTED_FORMATS:
        format = 'png'

    upper = parameters.get('upper')

    try:
        image = graph.generate( start, end, format=format, upper=upper)
    except ValueError, e:
        raise bottle.HTTPError( 400, e)

    content_type = SUPPORTED_FORMATS[format]
    bottle.response.set_header( 'Content-type', content_type)

    return image

TIMESPANS = {
        'hour': 3600,
        'day' : 24 * 3600,
        'week' : 7 * 24 * 3600,
        'month' : 31 * 24 * 3600,
        'year' : 366 * 24 * 3600
        }

def _resolve_timespan( timespan_name, start, end):
    timespan = TIMESPANS.get( timespan_name) or TIMESPANS['hour']
    if start and end:
        return str( start), str(end)
    elif start and timespan:
        return start, 'start+%s' % timespan
    else:
        return '-' + str(timespan), ''

if __name__ == '__main__':
    bottle.debug( True)
    bottle.run()
