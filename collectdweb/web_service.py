#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bottle

from collectdweb.models import Host, Plugin
from collectdweb.plugins import DumpInJSON, GroupBy, Urlizer, FilterObjectList, Detect404

detect_404 = Detect404()
filter_list = FilterObjectList()
dump_json =  DumpInJSON()

application = bottle.Bottle( autojson=False)
application.install(dump_json)

def split( name):
    return name.split( '-', 1) if '-' in name else ( name, None)

@application.route('/hosts/', apply=[ Urlizer('/hosts/{0.full_name}/'), GroupBy(), filter_list, detect_404, ])
def list_hosts():
    return Host.objects.all()

@application.route('/hosts/<host_name>/', apply=[
    Urlizer('/hosts/{0.host.full_name}/{0.full_name}/'),
    GroupBy('-'),
    filter_list, detect_404 ])
def list_plugins( host_name):
    return Host.objects.get( host_name).plugins.all()

@application.route('/hosts/<host_name>/<plugin>/', apply=[
    Urlizer( '/hosts/{0.plugin.host.full_name}/{0.plugin.full_name}/{0.full_name}.png'),
    detect_404, filter_list,
    ])
def list_graphs( host_name, plugin):
    plugin_name, plugin_instance = split( plugin)
    try:
        host = Host.objects.get( host_name)
        if not plugin_instance:
            plugins = [ plugin
                    for plugin in host.plugins.all()
                    if plugin.name == plugin_name ]
        elif plugin_instance[-1] == '*'  :
            prefix = plugin_instance.rstrip('*')
            if prefix:
                plugins = [ plugin for plugin in host.plugins.all()
                        if plugin.name == plugin_name and
                        plugin.instance and
                        plugin.instance.startswith( prefix) ]
            else:
                plugins = [ host.plugins.get(plugin_name, plugin_instance) ]
        else:
            plugins = [ host.plugins.get(plugin_name, plugin_instance) ]
    except Plugin.DoesNotExist:
        plugins = []

    graphes = []
    for plugin in plugins:
        graphes.extend( plugin.graphes.all() )

    graphes.sort( key=lambda x:( x.plugin.full_name, x.full_name))

    return graphes


