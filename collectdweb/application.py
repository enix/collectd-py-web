#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bottle

from collectdweb.models import Host, Plugin, Graph
from collectdweb.plugins import DumpInJSON, Signature

dump_json =  DumpInJSON()
signature = Signature()

SUPPORTED_FORMATS = {
        'pdf': 'application:pdf',
        'eps': 'application/epd', 
        'svg': 'image/svg+xml',
        'png': 'image/png'
        }
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

def split( name):
    return name.split( '-', 1) if '-' in name else ( name, None)

def get_url( graph):
    return '/graph/{host}/{plugin}/{graph_name}.png'.format(
            host = graph.plugin.host.name,
            plugin = graph.plugin.full_name,
            graph_name = graph.full_name
            )

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

@bottle.route('/hosts/<host_name>/<plugin>/', apply=dump_json)
def list_graphs( host_name, plugin):
    plugin_name, plugin_instance = split( plugin)
    try:
        host = Host.objects.get( host_name)
        if plugin_instance is None:
            plugins = [ plugin 
                    for plugin in host.plugins.all()
                    if plugin.name == plugin_name ]
        else:
            plugins = [ host.plugins.get(plugin_name, plugin_instance) ]
    except Host.DoesNotExist:
        raise bottle.HTTPError( 404, 'Host %s does not exist' % host_name)
    except Plugin.DoesNotExist:
        plugins = []

    graphes = []
    for plugin in plugins:
        graphes.extend( plugin.graphes.all() )

    return [ get_url( graph) for graph in graphes ]

@bottle.route('/sign/<path:path>', apply=dump_json)
def get_sign( path):
    url = '/exports/' + path
    return {
            'path' : url + '?sign='+ signature.sign( url)
            }

@bottle.route('/graph/<host_name>/<plugin>/<type>.png')
@bottle.route('/exports/graph/<host_name>/<plugin>/<type>.png', apply=signature)
def show_graph( host_name, plugin, type ):
    plugin_name, plugin_instance = split( plugin)
    type_name, type_instance = split( type)

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


if __name__ == '__main__':
    bottle.debug( True)
    bottle.run()
