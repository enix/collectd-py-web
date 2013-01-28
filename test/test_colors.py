#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from collectdweb.colors import Color

class TestColor(unittest.TestCase):
    def test_random(self):
        c = Color.random()
        self.assertTrue( isinstance( c, Color))

    def test_diff_random(self):
        r1 = Color.random()
        r2 = Color.random()
        self.assertNotEquals( r1, r2)

    def test_color_red(self):
        red = Color( (1., 0, 0))
        self.assertEquals( str(red), '#ff0000')

    def test_color_pink(self):
        pink = Color( (1., .505, .505))
        self.assertEquals( str(pink), '#ff8080')

    def test_from_string_hash(self):
        blue = Color.from_string( '#0050ff')
        self.assertEquals( str(blue), '#0050ff')

    def test_from_string(self):
        blue = Color.from_string( '0050ff')
        r, g, b = blue.rgb
        self.assertEquals( r, 0)
        self.assertTrue( 0.313 < g < 0.314 )
        self.assertEquals( b, 1.0)
        self.assertEquals( str(blue), '#0050ff')

class TestFaded( unittest.TestCase):
    def setUp( self):
        self.green = Color.from_string( '00ff00')
        self.faded_green = self.green.faded()

    def test_nomod(self):
        self.assertEquals( str(self.green), '#00ff00')

    def test_faded(self):
        self.assertTrue( isinstance( self.faded_green, Color))
        self.assertEquals( str( self.faded_green), '#bfffbf')





