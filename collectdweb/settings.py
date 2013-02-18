#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Settings file of the collectdweb web server.

.. data:: COLLECTD_CONFIG_FILE

    The path of the collection.conf file

.. data:: GRAPH_DEFINITIONS

    The path of a file containing graph definitions 

.. data:: RRDTOOL_BIN

    The absolute path to the rrdtool binary

"""


from collectdweb import get_shared

COLLECTD_CONFIG_FILE='/etc/collectd/collection.conf'
GRAPH_DEFINITIONS=get_shared( 'graph_definition')
RRDTOOL_BIN='rrdtool'

ADDRESS='0.0.0.0'
PORT=8080


try:
    from collectdweb.localsettings import *
except ImportError:
    pass
