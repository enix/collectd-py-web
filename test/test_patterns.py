#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest

from collectdweb.patterns import Filters, Filter, Is, Contains, EndsWith, StartsWith


class TestFilters(unittest.TestCase):
    def test_empty_filters(self):
        self.filters = Filters([ '*', '*', '*'])
        self.assertEquals( len(self.filters.patterns), 0)

class TestParse(unittest.TestCase):
    def test_parse_is( self):
        self.assertEquals( Filter( 'abc').pattern,
                [ Is('abc') ])

    def test_parse_startswith( self):
        self.assertEquals( Filter( 'abc*').pattern,
                [ StartsWith('abc') ])

    def test_parse_endswith( self):
        self.assertEquals( Filter( '*abc').pattern,
                [ EndsWith('abc') ])

    def test_parse_contains( self):
        self.assertEquals( Filter('*abc*').pattern,
                [ Contains( 'abc')])

    def test_parse_double_contains( self):
        self.assertEquals( Filter('*abc**').pattern,
                [ Contains( 'abc')])

    def test_parse_double_endswith( self):
        self.assertEquals( Filter('**abc').pattern,
                [ EndsWith( 'abc')])

    def test_parse_double_startswith( self):
        self.assertEquals( Filter('abc**').pattern,
                [ StartsWith( 'abc')])

    def test_parse_startswith_endswith( self):
        self.assertEquals( Filter( 'abc*def').pattern,
                [ StartsWith('abc'), EndsWith('def') ])

    def test_parse_startswith_contains_endswith( self):
        self.assertEquals( Filter( 'abc*def*ghi').pattern,
                [ StartsWith('abc'), Contains('def'), EndsWith('ghi') ])

    def test_parse_startswith_contains_contains_endswith( self):
        self.assertEquals( Filter( 'abc*def*ghi*jkl').pattern,
                [ StartsWith('abc'), Contains('def'), Contains('ghi'), EndsWith('jkl') ])

    def test_parse_contains_endswith( self):
        self.assertEquals( Filter( '*abc*def').pattern,
                [ Contains('abc'), EndsWith('def') ])

    def test_parse_startswith_contains( self):
        self.assertEquals( Filter( 'abc*def*').pattern,
                [ StartsWith('abc'), Contains('def') ])

class ExpectedMatch(object):
    def __init__(self, expected, result):
        self.expected = expected
        self.result = result
    def match( self, word, start):
        if word[start:] != self.expected:
            raise ValueError, '{word} is not {expected}'.format(
                    word=word, expected =self.expected)
        return self.result

class TestMatch(unittest.TestCase):
    def test_consumes(self):
        f = Filter('x')
        f.pattern = [ ExpectedMatch('abcdef', 3), ExpectedMatch( 'def', 3) ]

        self.assertTrue( f.match( 'abcdef'))

    def test_consumes_false(self):
        f = Filter('x')
        f.pattern = [ ExpectedMatch('abcdef', 0), ExpectedMatch( 'def', 3) ]

        self.assertFalse( f.match( 'abcdef'))
        
    def test_filters_first(self):
        filters = Filters('')
        f1 = Filter('x')
        f1.pattern = [ ExpectedMatch('abcdef', 3), ExpectedMatch( 'def', 3) ]
        f2 = Filter('x')
        f2.pattern = [ ExpectedMatch('abcdef', 3), ExpectedMatch( 'ghi', 3) ]
        filters.patterns = [ f1, f2 ]

        self.assertTrue( filters.match( 'abcdef'))

    def test_filters_second(self):
        filters = Filters('')
        f1 = Filter('x')
        f1.pattern = [ ExpectedMatch('abcdef', 3), ExpectedMatch( 'def', 0) ]
        f2 = Filter('x')
        f2.pattern = [ ExpectedMatch('abcdef', 3), ExpectedMatch( 'def', 3) ]
        filters.patterns = [ f1, f2 ]

        self.assertTrue( filters.match( 'abcdef'))

    def test_filters_none(self):
        filters = Filters('')
        f1 = Filter('x')
        f1.pattern = [ ExpectedMatch('abcdef', 3), ExpectedMatch( 'def', 0) ]
        f2 = Filter('x')
        f2.pattern = [ ExpectedMatch('abcdef', 3), ExpectedMatch( 'def', 0) ]
        filters.patterns = [ f1, f2 ]

        self.assertFalse( filters.match( 'abcdef'))

    def test_filters_nothing(self):
        filters = Filters([ '*' ])
        self.assertTrue( filters.match( 'anything' ))

class TestIs(unittest.TestCase):
    def test_is_not(self):
        self.assertEquals( Is('abc').match( 'abcdef', 0), 0)
    def test_is(self):
        self.assertEquals( Is('abc').match( 'abc', 0), 1)

class TestContains(unittest.TestCase):
    def test_contains(self):
        c = Contains( 'abc')
        self.assertEquals( c.match( '__abc_abc___abc', 0), 5)
    def test_contains_exact(self):
        c = Contains( 'abc')
        self.assertEquals( c.match( '__abc_abc___abc', 2), 3)
    def test_contains_at(self):
        c = Contains( 'abc')
        self.assertEquals( c.match( '__abc_abc___abc', 5), 4)
    def test_contains_on(self):
        c = Contains( 'abc')
        self.assertEquals( c.match( '__abc_abc___abc', 3), 6)

    def test_no_cotains(self):
        c = Contains( 'def')
        self.assertEquals( c.match( '__abc_abc___abc', 3), 0)
    def test_no_cotains_at(self):
        c = Contains( 'def')
        self.assertEquals( c.match( '__abc_def', 7), 0)

class TestStartsWith( unittest.TestCase):
    def test_match(self):
        s = StartsWith( 'abc')
        self.assertEquals( s.match( 'abcdef',0), 3)

    def test_no_match(self):
        s = StartsWith( 'def')
        self.assertEquals( s.match( 'abcdef',0), 0)

class TestEndsWith( unittest.TestCase):
    def test_match_at(self):
        e = EndsWith( 'def')
        self.assertEquals( e.match( 'abcdef', 3), 1)
    def test_match(self):
        e = EndsWith( 'def')
        self.assertEquals( e.match( 'abcdef', 0), 1)
    def test_no_match(self):
        e = EndsWith( 'def')
        self.assertEquals( e.match( 'abcdefghi', 0), 0)
    def test_no_match_after(self):
        e = EndsWith( 'def')
        self.assertEquals( e.match( 'abcdef', 4), 0)
