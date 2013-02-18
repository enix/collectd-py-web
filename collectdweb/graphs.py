#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict

from gevent import subprocess
from collectdweb.colors import Color
from collectdweb import settings

#Generer les graphes de cpu-*

class Library(object):
    """
    :param graphes: A dict of graphes definitions.
    :param aliases: A dict of alises and their target

    A list of graphes definitions
    """
    def __init__(self, graphes=None, aliases=None):
        self.graphes = graphes or {}
        self.aliases = aliases or {}
    def __len__(self):
        return len( self.graphes) + len( self.aliases)
    def register(self, name, graph):
        """
        :param name: name of the graph
        :param graph: definition of the graph

        Register a graph
        """
        self.graphes[ name]= graph
    def register_alias(self, name, target):
        """
        Register an alias *name* pointing to *target*
        """
        self.aliases[ name]= target

    def get(self, graph_name):
        """
        Get a graph for the name *graph_name*
        """
        graph_name = self.aliases.get( graph_name, graph_name)
        return self.graphes.get( graph_name)
    def dump(self, out):
        for name, graph in self.graphes.items():
            graph.dump( out, name)
        for alias, target in self.aliases.items():
            out.write( 'ALIAS %s = %s\n'% ( alias, target))

class RrdCommand( object):
    """
    :param *args: arguments to the rrdtool

    Subprocess invokation of the rrdtool utility.
    Iterate over the object to retrieve the results
    """
    def __init__( self, *args):
        command = [ settings.RRDTOOL_BIN ]
        command.extend( args)
        self.process = subprocess.Popen( command, **self.get_command_kwargs())

    def get_command_kwargs(self):
        """
        Return the kwargs for the subprocess invokation
        """
        return {
                'stdin': open('/dev/null'),
                'stdout': subprocess.PIPE,
                'stderr': subprocess.PIPE,
        }

class RrdFetch(RrdCommand):
    """
    :param file: RRD file to analyze
    :param reduce: reduce function to fecth
    :param \*args: options to the rrdtool

    Invokation of the fetch feature of rrdtool
    """
    def __init__( self, file, reduce, *args):
        super(RrdFetch, self).__init__( 'fetch', file, reduce, *args)

    def get_command_kwargs( self):
        kwargs = super( RrdFetch, self).get_command_kwargs()
        kwargs.update({
            'env' : {
                'LC_ALL': 'C'
                }
            })
        return kwargs

    def __iter__(self):
        return iter( self.process.stdout)

class RrdGraph( RrdCommand):
    """
    :param args: graph defintion

    Generates a graph.
    """
    def __init__(self, *args):
        super(RrdGraph, self).__init__( 'graph', '-', *args)
        first = self.first = self.process.stdout.read(3)
        if not first:
            err = self.process.stderr.read()
            if err:
                raise ValueError, err

    def __iter__(self):
        try:
            yield self.first
            while True:
                x = self.process.stdout.read(4000)
                yield x
                if x == '':
                    break
        finally:
            self.process.wait()

class BaseGraph( object):
    """
    Base class for a graph definition.

    Override :meth:`get_args` to implement a custom graph class.

    :param options: A dict of options for this graph
    """

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

    def get_max(self, sources, start, end):
        """
        :param sources: a list of rrd source, as tuples of 
            (plugin, instance, rrdfile)

        Extract the maximum of the *sources* between *start* and *end*
        """
        maxes = defaultdict( lambda :float('-inf'))
        for plugin, instance, file in sources:
            maxes = dict( (key, max( value, maxes[key] ))
                    for key, value in self._get_max( file, start, end) )
        return maxes

    def _get_max(self, file, start, end):
        command = RrdFetch( file, 'AVERAGE',
            '-s', start,
            '-e', end,
            )
        output = iter( command)
        header = next( output)
        labels = filter( bool, header.strip().split(' '))
        maxes = [ float('-inf')] * len( labels)
        for line in output:
            line = line.strip()
            if not line:
                continue
            values = map( float, filter( bool, line.split(':',1)[1].split(' ')))
            maxes = [ max(x,y) for x,y in  zip( maxes, values ) ]
        return zip( labels, maxes)

    def dump(self, out, name):
        out.write('%s %s\n' % ( self.__class__.__name__, name ))
        opts = iter( self.opts)
        for param, value in zip( opts, opts):
            out.write( '    %s : "%s"\n' % (param, value))

    def build( self, title, sources, start, end=None, format=None, upper=None):
        """
        :param title: The title of the graph
        :param sources: the list of sources
        :param start: the start of the graph
        :param end: the end of the graph
        :param format: the format of the graph
        :param upper: the upper limit

        Build a graph againts the *sources*
        returns an iterable of binary data
        """
        #sources: [ [ plugin, instance, file ] ... ]
        args = [
                '-a', format.upper() if format and format != 'text' else 'PNG',
                '-t', title,
                '-s', start,
                ]
        if end:
            args.extend([ '-e', end ])
        if upper: 
            args.extend([ '--upper-limit', upper ])

        args.extend( self.DEFAULT_OPTIONS)
        args.extend( self.opts )
        args.extend( self.get_args( [ ( p.replace('.', '-'), i, f) for p, i, f in sources ]))

        if format == 'text':
            return '\n'.join(args)

        graph = RrdGraph( *args)
        return graph

class Graph( BaseGraph):
    """
    A Graph representing a single rrd file.

    :param options: the options of a :class:`BaseGraph`
    :param definition: A list of instructions.
        Those instruction can contain a litteral `{file}` which
        will be replaced with the actual value when it's generated
    """
    list_type_instances = True
    def __init__( self, opts, definition):
        super( Graph, self).__init__( opts)
        self.definition = definition

    def file_definition(self):
        """
        Returns the list of the definitions importing a value from the file
        """
        return [ x for x in self.definition if x.startswith('DEF:') ]

    def graph_definition(self):
        """
        Returns the list of the definitions that do not get a value from a file
        """
        return [ x for x in self.definition if not x.startswith('DEF:') ]

    def get_args(self, sources):
        args=[]
        if len( sources) == 1:
            a, b, file = sources[0]
            args.extend([ x.format( file=file) for x in self.file_definition() ])
        else:
            for definition in self.file_definition():
                DEF,name,variable,reduction = definition.split(':')
                name,file = name.split('=')
                for plugin, instance_name, file in sources:
                    args.append( 'DEF:{name}_{instance}={file}:{variable}:{reduction}'.format(
                        name=name,
                        instance= plugin+'-'+instance_name,
                        file=file,
                        variable=variable,
                        reduction=reduction))

                args.append('CDEF:{name}={instances},{pluses}'.format(
                    name=name,
                    instances=','.join( name+'_'+p+'-'+i for p,i,f in sources ),
                    pluses=','.join( 'ADDNAN' for x in xrange( len( sources) - 1 ))
                    ))
        args.extend( self.graph_definition())
        return args


    def dump(self, out, name):
        super( Graph, self).dump( out, name)
        out.write( ''.join( '    ' + x + '\n' for x in self.definition))
        out.write( '\n')

class MetaGraph( BaseGraph):
    """
    A Graph representing values from different rrd files of the same plugin and plugin instance.

    :param types: A ordered list of types.
    :param colors: A dict binding a *type* to a color.
    """
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
            return [ type for type in reversed( self.types) if type in sources ]

    def get_args(self, all_sources):
        args = []
        data_sources = defaultdict(list)
        for plugin, inst_name, file in all_sources:
            data_sources[ inst_name].append(plugin)
            args.extend( x.format(
                inst_name=inst_name + '-' + plugin,
                file=file
                )
                for x in [
                    r'DEF:{inst_name}_min={file}:value:MIN',
                    r'DEF:{inst_name}_avg={file}:value:AVERAGE',
                    r'DEF:{inst_name}_max={file}:value:MAX',
                    ])

        for instance, sources in data_sources.items():
            for dim in [ 'min', 'avg', 'max' ]:
                if len(sources) > 1:
                    args.append( r'CDEF:{inst_name}_{dim}={sources},{pluses}'.format(
                        inst_name=instance,
                        dim=dim,
                        sources=','.join(instance+'-'+ source+'_'+dim for source in sources),
                        pluses=','.join( 'ADDNAN' for x in xrange( len( sources) - 1))
                        ))
                else:
                    args.append( r'CDEF:{inst_name}_{dim}={source},UN,0,{source},IF'.format(
                        inst_name=instance,
                        dim=dim,
                        source=instance+ '-' + sources[0] + '_' + dim
                        ))

        instance_names = self.sort_sources( data_sources)
        args.append( 'CDEF:{inst_name}_stk={inst_name}_avg'.format(
            inst_name=instance_names[0]
            ))
        args.extend( 'CDEF:{name}_stk={name}_avg,{previous_name}_stk,+'.format(
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
