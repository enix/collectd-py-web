#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bottle
from collectdweb import get_shared

application = bottle.Bottle()

index = get_shared( 'web')
@application.route('/')
def slash():
    return bottle.static_file( 'index.html', root=index)

medias = get_shared( 'web/media')
@application.route('/media/<path:path>')
def media(path):
    return bottle.static_file( path, root=medias)
