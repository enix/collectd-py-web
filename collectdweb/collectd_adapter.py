#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import itertools

def pad( lst, n):
    lst.extend( None for x in xrange(len(lst), n))
    return tuple( lst)

def get_dirs_inside( dirnames):
    for dirname in dirnames:
        try:
            listing = os.listdir( dirname)
        except OSError:
            continue
        for entry in listing:
            if entry[0] == '.':
                continue
            path = os.path.join( dirname, entry)
            if os.path.isdir( path):
                yield path, entry

def get_rrd_inside( dirname):
    try:
        listing = os.listdir( dirname)
        for entry in listing:
            if entry[0] == '.':
                continue
            if not entry.endswith( '.rrd'):
                continue
            yield entry
    except OSError:
        pass


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

    def get_all_hosts(self):
        return set( name for path,name in get_dirs_inside( self.datadirs ))

    def get_plugins_of(self, host):
        return set(
                pad( name.split('-',1), 2)
                for path, name  in self._get_plugins_instances( host))

    def _get_plugins_instances( self, host):
        return ( ( path,name)
                for path, name in get_dirs_inside(
                    os.path.join( datadir, host)
                    for datadir in self.datadirs
                    )
                )

    def _get_types(self, host, plugins):
        plugins = set( plugins)
        for path, name in self._get_plugins_instances( host):
            if name not in plugins:
                continue

            for rrd_file in get_rrd_inside( path):
                type_ = rrd_file.rsplit('.',1)[0]
                yield path, rrd_file, type_

    def get_graphes_of( self, host, plugin):
        return set( pad(type.split('-', 1), 2)
                for (path, rrd_file, type) in 
                self._get_types( host, [ plugin ])
                )

    def get_file(self, relative_path):
        for datadir in self.datadirs:
            abs_path = os.path.join( datadir, relative_path)
            if os.path.isfile( abs_path):
                return abs_path
        raise ValueError, 'Path %s does not exits' % relative_path

