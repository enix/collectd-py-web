#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
from cStringIO import StringIO

from collectdweb.parser import InStream, Parser


class TestInStream(unittest.TestCase):
    SAMPLE1 = '''line1
  

line2
    line3
  

'''
    SAMPLE2 = '''

    line1

    line2

line3'''

    SAMPLE3 = '''line1  \t
line2     
line3'''

    SAMPLE4=''
    SAMPLE5='''line1

line2
line3
line4

line5
'''
    SAMPLE6='''
line1

line2
line3
line4
'''

    def test_sample1(self):
        self.assertEquals( list( InStream( StringIO(self.SAMPLE1))),
                [ 'line1', '', 'line2', 'line3', '' ])

    def test_sample2(self):
        self.assertEquals( list( InStream( StringIO(self.SAMPLE2))),
                [ 'line1', '', 'line2', '', 'line3' ])

    def test_sample3(self):
        self.assertEquals( list( InStream( StringIO(self.SAMPLE3))),
                [ 'line1', 'line2', 'line3' ])

    def test_sample4_empty(self):
        self.assertEquals( list( InStream( StringIO(self.SAMPLE4))),
                [])

    def test_line1(self):
        x = InStream( StringIO(self.SAMPLE1))
        self.assertEquals( [ x.current_line for line in x ],[ 1, 2, 4, 5, 6 ])

    def test_line2(self):
        x = InStream( StringIO(self.SAMPLE2))
        self.assertEquals( [ x.current_line for line in x ],[ 3, 4, 5, 6, 7 ])

    def test_line3(self):
        x = InStream( StringIO(self.SAMPLE3))
        self.assertEquals( [ x.current_line for line in x ],[ 1, 2, 3 ])

    def test_up_to_new_line5(self):
        x = InStream( StringIO(self.SAMPLE5))
        next(x) # "line1"
        next(x) # ""
        next(x) # "line2"
        self.assertEquals( list( x.up_to_new_line()), [ 'line3', 'line4' ])
        self.assertEquals( next(x), 'line5')

    def test_up_to_new_line6(self):
        x = InStream( StringIO(self.SAMPLE6))
        next(x) # "line1"
        next(x) # ""
        next(x) # "line2"
        self.assertEquals( list( x.up_to_new_line()), [ 'line3', 'line4' ])

class Graph(object):
    def __init__(self, options, definition):
        self.options = options
        self.definition = definition

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser( classes={
            'Graph' : Graph 
            })
    def test_parser(self):
        library = self.parser.parse( StringIO('''
        Graph g1
            --option: "value"
            DEF:definition1
            DEF:definition2
            DEF:definition3

        Graph g2
            --option:
            DEF:definition1
            DEF:definition2

        ALIAS g3 = g2
        ALIAS g4 = g1

'''))
        self.assertEquals( len( library), 4)

        g1 = library.get('g1')
        self.assertIsInstance( g1, Graph)
        self.assertEquals( g1.options, { '--option': 'value'})
        self.assertEquals( g1.definition, [
            'DEF:definition1',
            'DEF:definition2',
            'DEF:definition3',
            ])

        g2 = library.get('g2')
        self.assertIsInstance( g2, Graph)
        self.assertEquals( g2.options, { '--option': ''})
        self.assertEquals( g2.definition, [
            'DEF:definition1',
            'DEF:definition2',
            ])

        g3 = library.get('g3')
        self.assertEquals( g2, g3)

        g4 = library.get('g4')
        self.assertEquals( g1, g4)

    def test_empty(self):
        library = self.parser.parse( StringIO())
        self.assertEquals( len( library), 0)

    def test_bad_alias_line(self):
        with self.assertRaises( ValueError):
            self.parser.parse( StringIO('''
            ALIAS g1=
    '''))
        with self.assertRaises( ValueError):
            self.parser.parse( StringIO('''
            ALIAS g1 : g2
    '''))


    def test_bad_graph_line(self):
        with self.assertRaises( ValueError):
            self.parser.parse( StringIO('''
            Graph
                DEF:definition1
    '''))
        with self.assertRaises( ValueError):
            self.parser.parse( StringIO('''
            Graph g1 alsogarbage
                DEF:definition1
    '''))

    def test_bad_option(self):
        with self.assertRaises( ValueError):
            self.parser.parse( StringIO('''
            Graph g1
                --option
                DEF:definition1
    '''))

    def test_empty_graph(self):
        library = self.parser.parse( StringIO('''
            Graph g1
            '''))
        self.assertEquals( len( library), 1)

    def test_undefinded_graph_class(self):
        with self.assertRaises( ValueError):
            self.parser.parse( StringIO('''
            OtherGraph g1
            '''))

    def test_non_alias_line_in_alias_block(self):
        with self.assertRaises( ValueError):
            self.parser.parse( StringIO('''
            ALIAS g1 = g2
            Graph mpm
            '''))

