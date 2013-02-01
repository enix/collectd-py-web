#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

key_files = [
        '/etc/collectd-py-web',
        os.path.expanduser('~/.collectd-py-webrc')
        ]

def get_key():
    return _get_saved_key() or _gen_and_save_key()

def _get_saved_key():
    for key_file in key_files:
        try:
            return open( key_file , 'rb').read()
        except IOError:
            pass

def _gen_and_save_key():
    import random, string
    key = ''.join( random.choice(string.letters) for x in xrange(64))
    _save(key)
    return key

def _save(key):
    for key_file in key_files:
        try:
            with open( key_file, 'wb' ) as file:
                file.write( key)
                os.fchmod( file.fileno(), 0600)
            break
        except IOError:
            continue
    else:
        return

