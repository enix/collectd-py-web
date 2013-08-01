#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from cStringIO import StringIO

from collectdweb.graphs import MetaGraph


class TestMetaGraph(unittest.TestCase):
    def test_load(self):
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
