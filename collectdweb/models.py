#!/usr/bin/env python
# -*- coding: utf-8 -*-

import settings

from collectdweb.collectd_adapter import Collectd
from collectdweb.parser import Parser
from collectdweb import get_shared
from collections import defaultdict

collectd = Collectd( settings.COLLECTD_CONFIG_FILE)
GRAPHS = Parser().parse( open( get_shared( 'graph_definition'), 'rb'))

class DoesNotExist(Exception):
    pass

class HostManager(object):
    def __iter__(self):
        return iter( collectd.get_all_hosts())
    def all( self):
        return [ Host(name) for name in self ]
    def names(self):
        return list(self)
    def get(self, name):
        if name in self:
            return Host( name)
        raise Host.DoesNotExist, name

class PluginManager( object):
    def __init__(self, host):
        self.host = host
    def __iter__(self):
        return iter( collectd.get_plugins_of( self.host.name ))
    def all(self):
        return [ Plugin( self.host, name, instance ) for name, instance in self ]
    def get(self, plugin, plugin_instance=None):
        if (plugin, plugin_instance) in self:
            return Plugin( self.host, plugin, plugin_instance)
        raise Plugin.DoesNotExist, plugin + (
                '-' + plugin_instance if plugin_instance else '' )

class GraphManager( object):
    def __init__(self, plugin):
        self.plugin = plugin
    def __iter__(self):
        sources = collectd.get_graphes_of( self.plugin.host.name, self.plugin.get_filename())
        graphes = defaultdict(list)

        for graph, instance in sources:
            graphes[graph].append( instance)

        for graph, instances in graphes.items():
            if GRAPHS.get( graph).list_type_instances:
                for i in instances:
                    yield graph, i
            else:
                yield graph, instances

    def all(self):
        return [ Graph( self.plugin, type_, type_instance)
                for type_, type_instance in  self ]

    def get(self, type_, type_instance=None):
        if type_instance is not None:
            if (  type_, type_instance) in self:
                return Graph( self.plugin, type_, type_instance)
        else:
            for type, type_instance in self:
                if type == type_ and not isinstance(type_instance, basestring):
                    return Graph( self.plugin, type_, type_instance)
        raise Graph.DoesNotExist, type_

class Host(object):
    objects = HostManager()
    def __init__(self, name):
        self.name = name

    @property
    def plugins(self):
        return PluginManager( self)

    class DoesNotExist( DoesNotExist):
        pass

    def get_path( self):
        return self.name

    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        return (self is other) or ( self.__class__ is other.__class__ and self.name == other.name )
    def __ne__(self, other):
        return not (self == other)
    def __repr__(self):
        return '<Host %s>' % self.name #pragma: no cover

class Plugin(object):
    def __init__(self, host, plugin, plugin_instance):
        self.host = host
        self.name = plugin
        self.instance = plugin_instance

    @property
    def graphes(self):
        return GraphManager( self)

    class DoesNotExist( DoesNotExist):
        pass

    @property
    def full_name(self):
        return self.name + ( '-' + self.instance if self.instance else '')

    @property
    def title(self):
        return self.host.name + '/' + self.full_name

    def get_path( self):
        return self.host.get_path() + '/' + self.get_filename()
    def get_filename( self):
        return self.name + ( '-' + self.instance if self.instance else '' )

    def __hash__(self):
        return hash( (self.name, self.instance))
    def __eq__(self, other):
        return ( self is other ) or ( self.__class__ is other.__class__ and
                self.host == other.host and 
                self.name == other.name and 
                self.instance == other.instance )
    def __ne__(self, other):
        return not (self == other)
    def __repr__(self):
        return '<Plugin %s %s>' % ( self.name, self.instance or '') #pragma: nocover

class Graph(object):
    def __init__(self, plugin, type_, type_instance):
        self.plugin = plugin
        self.name = type_
        self.graphdef = GRAPHS.get( self.name)
        self.instance = ( type_instance
                if type_instance is None or isinstance( type_instance, basestring)
                else  frozenset( type_instance))

    def _has_no_instance(self):
        return self.instance is None
    def _is_single_file(self):
        return isinstance( self.instance, basestring)

    class DoesNotExist( DoesNotExist):
        pass

    @property
    def full_name(self):
        return self.name + ( '-' + self.instance if self._is_single_file() else '')

    @property
    def title(self):
        return '{plugin.title}/{type}'.format(
                plugin=self.plugin,
                type=self.full_name,
                )

    def generate(self, start, end, format=None):
        return self.graphdef.build( self.title, self.rrd_source(), start, end, format)

    def rrd_source(self):
        prefix_plugin = self.plugin.get_path() + '/'
        if self._has_no_instance():
            return ( self.name, collectd.get_file( prefix_plugin + self.name + '.rrd'))
        if self._is_single_file():
            graph_name = self.name + '-' + self.instance
            return ( graph_name, collectd.get_file( prefix_plugin + graph_name + '.rrd'))

        return [ ( instance, collectd.get_file( prefix_plugin + self.name + '-' + instance + '.rrd' ))
                for instance in self.instance ]

    def __repr__(self):
        return '<Graph %s %s>' % (
                self.name,
                self.instance
                if self.instance and self.graphdef.list_type_instances
                else ''
                )

    def __hash__(self):
        return hash(( self.name, self.plugin, self.instance))

    def __ne__(self,other):
        return not ( self == other)

    def __eq__(self, other):
        return ( self.__class__ is other.__class__ and 
                self.name == other.name and
                self.plugin == other.plugin and
                self.instance == other.instance
                )
