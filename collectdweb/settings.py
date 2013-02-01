#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collectdweb import get_shared

COLLECTD_CONFIG_FILE='/etc/collectd/collection.conf'
GRAPH_DEFINITIONS=get_shared( 'graph_definition')

ADDRESS='0.0.0.0'
PORT=8080
