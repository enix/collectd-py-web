#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

class Color(object):
    def __init__(self, rgb):
        self.rgb = tuple( rgb)

    def __repr__(self):
        return str(self) #pragma: nocover

    def __str__(self):
        return '#%02hx%02hx%02hx' % tuple( 0xff *x for x in self.rgb)

    @classmethod
    def from_string( cls, string):
        s = 1 if string[0] == '#' else 0
        return cls( (int(string[i:i+2],16) / 255. for i in xrange( s, s+6, 2)) )

    @classmethod
    def random( cls):
        return cls( (random.random() for x in xrange( 3)))

    def faded(self):
        alpha = 0.25
        return self.__class__( .75 + x*alpha
                for x in self.rgb )
