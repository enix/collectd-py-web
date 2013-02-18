#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bottle

from collectdweb.models import Host, Graph
from collectdweb.plugins import DumpInJSON, Signature, Detect404
from collectdweb.error import make_image
from collectdweb.key import get_key


signature = Signature( get_key())

application = bottle.Bottle()

SUPPORTED_FORMATS = {
        'pdf': 'application/pdf',
        'eps': 'application/epd', 
        'svg': 'image/svg+xml',
        'png': 'image/png',
        'text' : 'text/plain',
        }
TIMESPANS = {
        'hour': 3600,
        'day' : 24 * 3600,
        'week' : 7 * 24 * 3600,
        'month' : 31 * 24 * 3600,
        'year' : 366 * 24 * 3600
        }

def split( name):
    return name.split( '-', 1) if '-' in name else ( name, None)

def _resolve_timespan( timespan_name, start, end):
    timespan = TIMESPANS.get( timespan_name) or TIMESPANS['hour']
    if start and end:
        return str( start), str(end)
    elif start and timespan:
        return start, 'start+%s' % timespan
    else:
        return '-' + str(timespan), ''

@application.route('/sign/', apply=DumpInJSON())
def get_sign():
    urls = bottle.request.GET.getall( 'url')
    urls = ( '/export' + url for url in urls if url.startswith('/hosts/') )
    return [
             url + '?sign='+ signature.sign( url)
             for url in urls
            ]

@application.route('/hosts/<host_name>/<plugin>/<type>.png', apply=Detect404())
@application.route('/exports/hosts/<host_name>/<plugin>/<type>.png', apply=[ signature, Detect404()])
def show_graph( host_name, plugin, type ):
    plugin_name, plugin_instance = split( plugin)
    type_name, type_instance = split( type)

    graph = Host.objects.get( host_name
            ).plugins.get( plugin_name, plugin_instance
            ).graphes.get( type_name, type_instance)

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
    except Graph.NoDefinition, e:
        bottle.response.status = 400
        image = make_image( 'No Graph definition for %s' % str(e), format)
    except ValueError, e:
        bottle.response.status = 400
        import traceback
        traceback.print_exc(e)
        image = make_image( str(e), format)

    content_type = SUPPORTED_FORMATS[format]
    bottle.response.set_header( 'Content-type', content_type)

    return image

