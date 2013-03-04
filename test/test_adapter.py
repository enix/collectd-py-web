#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from test import get_fixture
from collectdweb.collectd_adapter import Collectd

class TestAdapterFromConfig(unittest.TestCase):
    def setUp(self):
        self.adapter = Collectd.from_config_file( get_fixture('collection.conf'))

    def test_datadirs(self):
        self.assertEquals( set(self.adapter.datadirs), set([
            '/home/collectdweb/fixtures/rrd1',
            '/home/collectdweb/fixtures/rrd2'
            ]))

    def test_libdir(self):
        self.assertEquals( set(self.adapter.libdirs), set([
            '/home/collectdweb/fixtures/libs',
            ]))

class TestAdadpterFromConfigEdgeCase(unittest.TestCase):
    def test_libdirs(self):
        self.adapter = Collectd.from_config_file( get_fixture('collection-wrong.conf'))
        self.assertEquals( self.adapter.libdirs, set())

class TestAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = Collectd([
            get_fixture('rrd1'),
            get_fixture('rrd2'),
            ])

    def test_hosts(self):
        self.assertEquals( set(self.adapter.get_all_hosts()),
                set([ 'host1', 'host2', 'host3']) )

    def test_plugin(self):
        self.assertEquals( set(self.adapter.get_plugins_of([ 'host2' ])),
                set([
                    ( 'interface', 'eth0'),
                    ( 'interface', 'eth1'),
                    ( 'interface', 'eth2'),
                    ( 'memory', None),
                    ( 'cpu', None),
                    ]))

    def test_graphs(self):
        self.assertEquals( set(self.adapter.get_graphes_of([ 'host2/interface-eth0' ])),
                set([
                    ('if_packets', None),
                    ('if_errors', None),
                    ]))

    def test_get_file(self):
        filepath = self.adapter.get_file( 'host1/irq/irq-3.rrd')
        self.assertEquals( filepath, get_fixture('rrd1/host1/irq/irq-3.rrd'))
        filepath = self.adapter.get_file( 'host2/interface-eth1/if_packets.rrd')
        self.assertEquals( filepath, get_fixture('rrd2/host2/interface-eth1/if_packets.rrd'))

    def test_errors(self):
        self.assertEquals( set(self.adapter.get_plugins_of([ 'host3' ])),
                set())

    def test_inexisting_file(self):
        with self.assertRaises( ValueError):
            self.adapter.get_file( 'host1/irq/irq-4.rrd')

