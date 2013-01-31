#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Filters(object):
    def __init__(self, patterns):
        self.patterns = [ Filter( pattern)
                for pattern in patterns
                if pattern and pattern != '*'
                ]

    def match( self, word):
        if not self.patterns:
            return True
        for pattern in self.patterns:
            if pattern.match( word):
                return True
        return False

class Filter(object):
    def __init__(self, pattern):
        self.pattern = list( self.parse( pattern ))

    def __repr__(self):
        return '+'.join( map( repr, self.pattern))

    def match(self, string):
        start = 0
        for pattern in self.pattern:
            forward = pattern.match( string, start)
            if forward == 0:
                return False
            else:
                start += forward
        return True

    def parse(self, pattern):
        tokens = pattern.split('*')
        for start, token, end in zip( xrange(len(tokens)), tokens, xrange( -len(tokens)+1, 1)):
            if end == 0 :
                if start == 0:
                    yield Is(token)
                elif token:
                    yield EndsWith( token)
            elif start == 0:
                if token:
                    yield StartsWith( token)
            elif token:
                yield Contains(token)

class Pattern(object):
    def __init__(self, target):
        self.target = target
    def __repr__(self):
        return '%s(%s)' % ( self.__class__.__name__, self.target)

class Is(Pattern):
    def match(self, word, start):
        return word == self.target and 1 or 0

class Contains(Pattern):
    def match(self, word, start):
        return len(self.target) if word.find( self.target, start) != -1 else 0

class EndsWith(Pattern):
    def match(self, word, start):
        if start + len(self.target) > len(word):
            return 0
        return word.endswith( self.target) and 1 or 0
class StartsWith(Pattern):
    def match(self, word, start):
        return word.startswith( self.target) and len( self.target)


