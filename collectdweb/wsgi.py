#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import gevent.monkey
    gevent.monkey.patch_all()
except ImportError:
    pass

from bottle import Bottle
from collectdweb.application import application as images
from collectdweb.web_service import application as web_service
from collectdweb.statics import application as statics


application = Bottle()

application.merge( images )
application.merge( web_service )
application.merge( statics)
