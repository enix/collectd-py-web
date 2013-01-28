#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
from colors import Color
from collectdweb import get_shared

#Generer les graphes de cpu-*

class Library(object):
    def __init__(self, graphes=None, aliases=None):
        self.graphes = graphes or {}
        self.aliases = aliases or {}
    def __len__(self):
        return len( self.graphes) + len( self.aliases)
    def register(self, name, graph):
        self.graphes[ name]= graph
    def register_alias(self, name, target):
        self.aliases[ name]= target

    def get(self, graph_name):
        graph_name = self.aliases.get( graph_name, graph_name)
        return ( self.graphes.get( graph_name) or FakeGraph())
    def dump(self, out):
        for name, graph in self.graphes.items():
            graph.dump( out, name)
        for alias, target in self.aliases.items():
            out.write( 'ALIAS %s = %s\n'% ( alias, target))

class FakeGraph(object):
    list_type_instances = True
    error_file = get_shared( 'icons/error.png')
    def build( self, title, sources, start, end, format=None):
        return open( self.error_file, 'rb')

class RrdCommand( object):
    def __init__(self, args):
        command = [ 'rrdtool' ]
        command.extend( args)
        self.process = subprocess.Popen( command,
                env={
                    'TZ' : 'UTC'
                    },
                stdin=open('/dev/null'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        error = self.process.stderr.read()
        if error:
            raise ValueError, error

    def __iter__(self):
        for x in self.process.stdout:
            yield x
        self.process.wait()

class BaseGraph( object):
    DEFAULT_OPTIONS = [
            '--rigid',
            '-w', '500',
            '-h', '160',
            '--alt-autoscale-max',
            '--lower-limit', '0',
            '--slope-mode',
            '--font', 'TITLE:10:Monospace',
            '--font', 'AXIS:8:Monospace',
            '--font', 'LEGEND:8:Monospace',
            '--font', 'UNIT:8:Monospace',
            '-c', 'BACK#FF000000',
            '-c', 'SHADEA#FF000000',
            '-c', 'SHADEB#FF000000',
            '-i' ]

    def __init__(self, options):
        self.opts = []
        if options:
            for option_pair in options.iteritems():
                self.opts.extend( option_pair)

    def dump(self, out, name):
        out.write('%s %s\n' % ( self.__class__.__name__, name ))
        opts = iter( self.opts)
        for param, value in zip( opts, opts):
            out.write( '    %s : "%s"\n' % (param, value))

    def build( self, title, sources, start, end=None, format=None):
        args = [
                'graph',
                '-',
                '-a', format.upper() if format else 'PNG',
                '-t', title,
                '-s', start,
                ]
        if end:
            args.extend([ '-e', end ])

        args.extend( self.DEFAULT_OPTIONS)
        args.extend( self.opts )
        args.extend( self.get_args(sources))
        
        graph = RrdCommand(args)
        return graph

class Graph( BaseGraph):
    list_type_instances = True
    def __init__( self, opts, definition):
        super( Graph, self).__init__( opts)
        self.definition = definition

    def get_args(self, source):
        instance_name, file = source
        return [ x.format( file=file)
                for x in self.definition ]

    def dump(self, out, name):
        super( Graph, self).dump( out, name)
        out.write( ''.join( '    ' + x + '\n' for x in self.definition))
        out.write( '\n')

class MetaGraph( BaseGraph):
    list_type_instances = False
    default_number_format = '%6.1lf'

    def __init__(self, opts, types, colors):
        self.number_format = opts.pop('--number_format', self.default_number_format)
        super( MetaGraph, self).__init__( opts)
        self.types = types
        self.colors = { instance: Color.from_string( color)
                for instance, color in colors.items() } if colors else {}

    @classmethod
    def load( cls, opts, definitions):
        colors = {}
        types = []
        try:
            for definition in definitions:
                type, color = ( x.strip() for x in definition.split( ':', 1))
                types.append( type)
                if color:
                    colors[type] = color
        except ValueError:
            raise ValueError, 'Bad definition line'
        return cls( opts, types, colors)

    def dump(self, out, name):
        super( MetaGraph, self).dump( out, name)
        if self.number_format != self.default_number_format:
            out.write( '    --number_format: "%s"\n' % self.number_format)
        if self.types:
            out.write( ''.join('    %s: %s\n' % ( x, self.colors.get(x, ''))
                    for x in self.types))
        out.write( '\n')


    def sort_sources( self, sources):
        if not self.types:
            return list( sources)
        else:
            instances = dict( sources)
            sources_ = list()
            for type in reversed( self.types):
                if type in instances:
                    sources_.append(( type, instances[type]))
            return sources_

    def get_args(self, sources):
        args = []
        sources = self.sort_sources(sources)
        for inst_name, file in sources:
            args.extend( x.format( inst_name=inst_name, file=file)
                    for x in [
                        r'DEF:{inst_name}_min={file}:value:MIN',
                        r'DEF:{inst_name}_avg={file}:value:AVERAGE',
                        r'DEF:{inst_name}_max={file}:value:MAX',
                        r'CDEF:{inst_name}_nnl={inst_name}_avg,UN,0,{inst_name}_avg,IF',
                        ])

        instance_names = [ x[0] for x in sources ]
        args.append( 'CDEF:{inst_name}_stk={inst_name}_nnl'.format(
            inst_name=instance_names[0]
            ))
        args.extend( 'CDEF:{name}_stk={name}_nnl,{previous_name}_stk,+'.format(
            previous_name=previous_name,
            name=name)
            for previous_name, name in zip( instance_names, instance_names[1:] ) )

        number_format = self.number_format
        legend_length = max( len(x) for x in instance_names)
        for instance_name in reversed( instance_names):
            line_color = self.colors.get(instance_name) or Color.random()
            area_color = line_color.faded()
            legend = '%-*s' % ( legend_length, instance_name)

            args.extend( x.format(
                inst_name=instance_name,
                number_format=number_format,
                line_color=line_color,
                area_color=area_color,
                legend=legend,
                )
                for x in [
                    r'AREA:{inst_name}_stk{area_color}',
                    r'LINE1:{inst_name}_stk{line_color}:{legend}',
                    r'GPRINT:{inst_name}_min:MIN:{number_format} Min,',
                    r'GPRINT:{inst_name}_avg:AVERAGE:{number_format} Avg,',
                    r'GPRINT:{inst_name}_max:MAX:{number_format} Max,',
                    r'GPRINT:{inst_name}_avg:LAST:{number_format} Last\l',
                    ])
        return args
