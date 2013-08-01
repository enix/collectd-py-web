#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import mock
from cStringIO import StringIO
from test import get_fixture

from collectdweb.graphs import Graph, MetaGraph, RrdFetch


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.graph = Graph({}, [
            'DEF:avg={file}:value:AVERAGE',
            'DEF:max={file}:value:MAX',
            'AREA:max#DFB7F7',
            'LINE1:avg#A000FF:Count ',
            'GPRINT:avg:LAST:%4.1lf Last\l',
        ])

    def test_get_max(self):
        rrdfetch = StringIO("""                             rx                  tx

1375279500: 3.6862865714e+04 1.7952737143e+04
1375279570: 2.2472217143e+04 7.2602942857e+03
1375279640: 8.5709051429e+04 1.8250851429e+04
1375365880: 1.1367948571e+04 5.8722485714e+03
1375365950: 1.1587417143e+04 1.0358848571e+04
1375366020: nan nan
""")
        with mock.patch('collectdweb.graphs.RrdFetch', spec=RrdFetch) as pRrdFetch:
            pRrdFetch.return_value.__iter__.return_value = iter(rrdfetch)
            max = self.graph.get_max([('', 'if_octets-eth0', 'interface/if_octets-eth0.rrd')], 1, 10)
            self.assertEqual(max, {'rx': 85709.051429, 'tx': 18250.851429})

    def test_get_args_single(self):
        args = self.graph.get_args([('', 'if_octets-eth0', 'interface/if_octets-eth0.rrd')])
        self.assertEqual(args, [
            'DEF:avg=interface/if_octets-eth0.rrd:value:AVERAGE',
            'DEF:max=interface/if_octets-eth0.rrd:value:MAX',
            'AREA:max#DFB7F7',
            'LINE1:avg#A000FF:Count ',
            'GPRINT:avg:LAST:%4.1lf Last\\l'
        ])

    def test_get_args_multiple(self):
        args = self.graph.get_args([
            ('', 'if_octets-eth0', 'interface/if_octets-eth0.rrd'),
            ('', 'if_octets-eth1', 'interface/if_octets-eth1.rrd'),
        ])
        self.assertEqual(args, [
            'DEF:avg_-if_octets-eth0=interface/if_octets-eth0.rrd:value:AVERAGE',
            'DEF:avg_-if_octets-eth1=interface/if_octets-eth1.rrd:value:AVERAGE',
            'CDEF:avg=avg_-if_octets-eth0,avg_-if_octets-eth1,ADDNAN',
            'DEF:max_-if_octets-eth0=interface/if_octets-eth0.rrd:value:MAX',
            'DEF:max_-if_octets-eth1=interface/if_octets-eth1.rrd:value:MAX',
            'CDEF:max=max_-if_octets-eth0,max_-if_octets-eth1,ADDNAN',
            'AREA:max#DFB7F7',
            'LINE1:avg#A000FF:Count ',
            'GPRINT:avg:LAST:%4.1lf Last\\l'
        ])


class TestMetaGraphLoad(unittest.TestCase):
    def test_load(self):
        mg = MetaGraph.load({}, StringIO('''free:
    cached:  
    buffered: 
    used:'''))

        self.assertEqual(mg.types, ['free', 'cached', 'buffered', 'used'])
        self.assertEqual(mg.colors, {})

    def test_load_color(self):
        mg = MetaGraph.load({}, StringIO('''free: #00e000
    cached: #0000ff
    buffered: #ffb000
    used: #ff0000'''))

        self.assertEqual(mg.types, ['free', 'cached', 'buffered', 'used'])
        self.assertEqual(mg.colors, {
            'free': '#00e000',
            'cached': '#0000ff',
            'buffered': '#ffb000',
            'used': '#ff0000',
        })
