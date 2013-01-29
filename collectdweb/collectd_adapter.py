#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import itertools

def pad( lst, n):
    lst.extend( None for x in xrange(len(lst), n))
    return tuple( lst)

class Collectd( object):
    def __init__(self, config_file):
        self.filename = config_file

        self._config_loaded = False
        self._filesystem = None

        self._libdirs = set()
        self._datadirs = set()

    def load_config_file( self):
        handle = open( self.filename, 'r')
        lines = (
                map( str.strip, line.split(':', 1))
                for line in itertools.imap( str.strip, handle)
                if not line.startswith( '#') and ':' in line
                )
        lines =(
                ( key.lower(), value[1:-1])
                for key, value in lines
                if key and value[0] == '"' and value[-1] == '"'
                )
        for key, value in lines:
            if key == 'libdir':
                if os.path.isdir( value):
                    self._libdirs.add( value)
            elif key == 'datadir':
                if os.path.isdir( value):
                    self._datadirs.add( value)
        self._loaded = True

    @property
    def datadirs(self):
        if not self._config_loaded:
            self.load_config_file()
        return self._datadirs
    @property
    def libdirs(self):
        if not self._config_loaded:
            self.load_config_file()
        self.load_config_file()
        return self._libdirs

    def get_inside( self, dirnames):
        for datadir in self.datadirs:
            for dirname in dirnames:
                try:
                    listing = os.listdir( os.path.join( datadir,  dirname))
                except OSError:
                    continue
                for entry in listing:
                    if entry[0] == '.':
                        continue
                    path = os.path.join( datadir, dirname, entry)
                    yield path, entry
    def get_dirs_inside( self, dirnames):
        for path, entry in self.get_inside( dirnames):
            if os.path.isdir( path):
                yield entry

    def get_rrd_inside( self, dirnames):
        for path, entry in self.get_inside( dirnames):
            if os.path.isfile( path) and entry.endswith( '.rrd'):
                yield entry

    def get_all_hosts(self):
        return set( name
                for name in self.get_dirs_inside(['']))

    def get_plugins_of(self, hosts ):
        return set( pad( name.split('-',1), 2)
                for name  in self.get_dirs_inside( hosts ))

    def get_graphes_of( self, plugins ):
        return set( pad(graph.rsplit('.',1)[0].split('-', 1), 2)
                for graph in self.get_rrd_inside( plugins))

    def get_file(self, relative_path):
        for datadir in self.datadirs:
            abs_path = os.path.join( datadir, relative_path)
            if os.path.isfile( abs_path):
                return abs_path
        raise ValueError, 'Path %s does not exits' % relative_path

