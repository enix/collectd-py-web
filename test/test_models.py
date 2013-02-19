#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from collectdweb.collectd_adapter import Collectd
from collectdweb import models
from collectdweb.models import Host, Plugin, Graph

models.collectd = Collectd( '/home/cecedille1/enix/collectd-py-web/test/fixtures/collection.conf')

class TestHost(unittest.TestCase):
    def test_equality(self):
        self.assertTrue( Host( 'host1') == Host('host1'))
        self.assertFalse( Host( 'host1') == Host('host2'))
    def test_not_equality(self):
        self.assertTrue( Host( 'host1') != Host('host2'))
        self.assertFalse( Host( 'host1') != Host('host1'))

class TestHosts( unittest.TestCase):
    def test_all_hosts(self):
       self.assertTrue( all( isinstance(x, Host) for x in Host.objects.all()))

    def test_once_all( self):
        self.assertTrue( isinstance( Host.objects.all(), list ))
        self.assertEquals( len( Host.objects.all()), 3)
        self.assertEquals( set( Host.objects.all()),
                set([
                    Host( 'host1'),
                    Host( 'host2'),
                    Host( 'host3'),
                    ]))

    def test_get(self):
        self.assertEquals( Host.objects.get( 'host1'), Host('host1') )
    def test_get_not(self):
        self.assertRaises( Host.DoesNotExist, Host.objects.get, 'host4')

class TestPlugin( unittest.TestCase):
    def setUp(self):
        self.host = Host.objects.get('host2')

    def test_title(self):
        p = Plugin( self.host, 'memory', None)
        self.assertEquals( p.title, 'host2/memory')

    def test_full_name_instance(self):
        p = Plugin( self.host, 'memory', None)
        self.assertEquals( p.full_name, 'memory')
    def test_full_name_no_instance(self):
        p = Plugin( self.host, 'interface', 'eth0')
        self.assertEquals( p.full_name, 'interface-eth0')

    def test_equality(self):
        p1 = Plugin( self.host, 'memory', None)
        p2 = Plugin( self.host, 'memory', None)
        p3 = Plugin( self.host, 'interface', 'eth0')
        self.assertTrue( p1 == p2)
        self.assertFalse( p1 != p2)
        self.assertTrue( p1 != p3)
        self.assertFalse( p1 == p3)

class TestPlugins( unittest.TestCase):
    def setUp(self):
        self.host = Host.objects.get('host2')

    def test_all_plugins(self):
        self.assertTrue( isinstance( self.host.plugins.all(), list))
        self.assertEquals( len( self.host.plugins.all()), 6)
        self.assertEquals( set( self.host.plugins.all()), set([
            Plugin( self.host, 'cpu', None),
            Plugin( self.host, 'memory', None),
            Plugin( self.host, 'interface', frozenset([ 'eth0', 'eth1', 'eth2'])),
            Plugin( self.host, 'interface', 'eth0'),
            Plugin( self.host, 'interface', 'eth1'),
            Plugin( self.host, 'interface', 'eth2'),
            ]))
    def test_get(self):
        self.assertEquals(
                self.host.plugins.get( 'interface', 'eth2'),
                Plugin( self.host, 'interface', 'eth2'))
        self.assertEquals(
                self.host.plugins.get( 'memory', None),
                Plugin( self.host, 'memory', None))
    def test_get_not(self):
        self.assertRaises( Plugin.DoesNotExist, self.host.plugins.get, 'interface', 'lo')
        self.assertRaises( Plugin.DoesNotExist, self.host.plugins.get, 'memory', 'dimm1')
        self.assertRaises( Plugin.DoesNotExist, self.host.plugins.get, 'ird', None)

class TestGraphes(unittest.TestCase):
    def setUp(self):
        host1 = Host.objects.get('host1')
        host2 = Host.objects.get('host2')
        self.eth0 = host2.plugins.get('interface', 'eth0')
        self.memory = host2.plugins.get( 'memory', None)
        self.irqs = host1.plugins.get( 'irq', None)

    def test_multi_type_no_instance(self):
        self.assertEquals( len( self.eth0.graphes.all()), 2)
        self.assertEquals( set( self.eth0.graphes.all()), set([
            Graph( self.eth0, 'if_errors', None),
            Graph( self.eth0, 'if_packets', None),
            ]))
        
    def test_type_ignore_instance(self):
        self.assertEquals( len( self.memory.graphes.all()), 1)
        self.assertEquals( set( self.memory.graphes.all()), set([
            Graph( self.memory, 'memory', [ 'used', 'free' ]),
            ]))

    def test_type_mutli_instance(self):
        self.assertEquals( len( self.irqs.graphes.all()), 3)

    def test_get_multi_instance( self):
        self.assertEquals( self.memory.graphes.get( 'memory'), 
                Graph( self.memory, 'memory', [ 'used', 'free' ]))

    def test_get_single_instance(self):
        self.assertEquals( self.irqs.graphes.get( 'irq', '3'), 
                Graph( self.irqs, 'irq', '3'))

    def test_get_not_single_instance(self):
        self.assertRaises( Graph.DoesNotExist, self.irqs.graphes.get, 'irq', '4')
        self.assertRaises( Graph.DoesNotExist, self.irqs.graphes.get, 'irq', None)

    def test_get_none(self):
        self.assertEquals( self.eth0.graphes.get( 'if_packets'), 
                Graph( self.eth0, 'if_packets', None))

class TestGraph(unittest.TestCase):
    def setUp(self):
        host1 = Host.objects.get('host1')
        host2 = Host.objects.get('host2')
        self.eth0 = host2.plugins.get('interface', 'eth0')
        self.memory = host2.plugins.get( 'memory', None)
        self.irqs = host1.plugins.get( 'irq', None)
    
    def test_full_name_no_instance(self):
        g = Graph( self.eth0, 'if_packets', None)
        self.assertEquals( g.full_name, 'if_packets')
    def test_full_name_instance(self):
        g = Graph( self.irqs, 'irq', '3')
        self.assertEquals( g.full_name, 'irq-3')

    def test_equality(self):
        g1a = Graph( self.eth0, 'if_packets', None)
        g1b = Graph( self.eth0, 'if_packets', None)
        g2a = Graph( self.eth0, 'interface', [ 'if_errors', 'if_packets'])
        g2b = Graph( self.eth0, 'interface', [ 'if_packets', 'if_errors'])

        self.assertTrue( g1a == g1b)
        self.assertTrue( g2a == g2b)
        self.assertTrue( g1a != g2a)
        self.assertFalse( g1a != g1a)

    def test_rrd_single_instance(self):
        self.assertEquals( Graph( self.irqs, 'irq', '3').rrd_source(),
                [ ('', 'irq-3', '/home/cecedille1/enix/collectd-py-web/test/fixtures/rrd1/host1/irq/irq-3.rrd') ]
                )

    def test_rrd_source_multi_instance(self):
        self.assertEquals( Graph( self.memory, 'memory', [ 'free', 'used'] ).rrd_source(), [
                ( '', 'used', '/home/cecedille1/enix/collectd-py-web/test/fixtures/rrd1/host2/memory/memory-used.rrd'),
                ( '', 'free', '/home/cecedille1/enix/collectd-py-web/test/fixtures/rrd1/host2/memory/memory-free.rrd'),
                ])
    def test_rrd_source(self):
        self.assertEquals( Graph( self.eth0, 'if_packets', None).rrd_source(),
                [ ('', 'if_packets', '/home/cecedille1/enix/collectd-py-web/test/fixtures/rrd1/host2/interface-eth0/if_packets.rrd' ) ]
        )


