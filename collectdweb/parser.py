#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collectdweb.graphs import Graph, MetaGraph, Library


__all__ = [ 'Parser', 'SyntaxError' ]

class SyntaxError( Exception):
    """
    Exception raised when the parsed file use an incorrect syntax
    """
    pass

class InStream(object):
    def __init__(self, stream):
        self.stream = stream
        self._was_previous_empty = True
        self.current_line = 0
    def __iter__(self):
        return self
    def next(self):
        line = self._next()
        if self._was_previous_empty:
            self._was_previous_empty = False
            while not line:
                line = self._next()
        else:
            self._was_previous_empty = not bool( line)
        return line

    def _next(self):
        self.current_line += 1
        return next( self.stream).strip()

    def up_to_new_line(self):
        for line in self:
            if not line:
                break
            yield line

class Context(object):

    def __init__(self, classes, library):
        self._classes = classes
        self._library = library
        self._reset()

    def _reset(self):
        self.class_= None
        self.name = None
        self.opts = {}

    def set_definition(self, definition):
        self._library.register( self.name, self.class_( self.opts, definition))
        self._reset()

    def set_graph_type(self, grah_type):
        self.class_ = self._classes[ grah_type]

    def set_name(self, name):
        self.name = name
    def set_option(self, param, value):
        self.opts[param] = value

    def set_alias(self, alias, target):
        self._reset()
        self._library.register_alias(alias, target)


class Parser(object):
    """
    Parse a file containing graph definitions
    by default generate :class:`~collectdweb.graphs.Graph` and :class:`~collectdweb.graphs.MetaGraph`

    :param classes: A dict of keyword pointing to a callable return a :class:`collectdweb.graphs.BaseGraph` subclass

    Syntax of the graph definition is:

    .. productionlist::
        graph_file: ( graph_definiton | alias_definition+ )
                  : empty_line
                  :
        graph_definiton: graph_class graph_name
                       : option_line +
                       : definition_line +
        option_line: "--" option_name ":" ("option_value") ?
                   :
        alias_definition: "ALIAS" alias_name "=" target
                        :
        target: A previously defined `graph_name`
        graph_class: A key of `classes`
        definition_line: depends on the `graph_class`
    """
    def __init__(self, classes=None):
        self._library = Library()
        self.classes = classes or {
            'Graph' : Graph,
            'MetaGraph' : MetaGraph.load
            }

    def parse(self, in_stream):
        """
        Parse a file-like object *in_stream* and returns a :class:`collectdweb.graphs.Library` instance
        with the content of the graphes.
        """
        stream = InStream(in_stream)
        context = Context( self.classes, self._library )
        try:
            while self.parse_graph( stream, context):
                pass
        except SyntaxError, e:
            raise ValueError, 'In %s at line %s: %s' % (
                    getattr(in_stream, 'name', '<input>'), stream.current_line, e)
        return self._library

    def parse_graph(self, stream, context):
        try:
            self.parse_first_line( stream, context)
        except StopIteration:
            return False
        return True
    
    def parse_first_line(self, stream, context):
        """
        """
        line = next(stream)

        tokens = ( token.strip() for token in line.split() if token.strip())
        name = next( tokens)
        if name == 'ALIAS':
            try:
                self.parse_alias( tokens, context)
                for line in stream.up_to_new_line():
                    tokens = ( token.strip() for token in line.split() if token.strip())
                    name = next( tokens)
                    if name != 'ALIAS' :
                        raise SyntaxError, 'Non ALIAS line in ALIAS block: %s' % line
                    self.parse_alias( tokens, context)
            except ValueError:
                raise SyntaxError, 'Misformed ALIAS line: %s' % line
        else:
            try:
                context.set_graph_type( name)
            except KeyError:
                raise SyntaxError, 'Graph Type %s is not defined' % name
            try:
                name, = tokens
            except ValueError:
                raise SyntaxError, 'Misformed graph line: %s' % line
            context.set_name( name)
            self.parse_definition( stream, context)

    def parse_alias( self, tokens, context):
        alias, equal, target = tokens
        if equal != '=':
            raise ValueError
        context.set_alias( alias, target) 

    def parse_definition( self, stream, context):
        for line in stream:
            if not line:
                context.set_definition([])
                return
            elif line.startswith( '-'):
                #option
                try:
                    param, value = ( x.strip() for x in line.split( ':', 1))
                except ValueError:
                    raise SyntaxError, 'Misformed option line: %s' % line
                if value and ( value[0] == "'" and value[-1] == "'" or 
                        value[0] == '"' and value[-1] == '"' ):
                    value = value[1:-1]
                context.set_option( param, value)
            else:
                definition = [ line ]
                definition.extend( stream.up_to_new_line())
                context.set_definition( definition)
                return
