#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cStringIO import StringIO
import textwrap
from collectdweb import get_shared

WIDTH=700
try:
    import PIL.Image
    import PIL.ImageDraw
    import PIL.ImageFont
    try:
        import fontconfig
    except ImportError:
        fontconfig = None
except ImportError:
    PIL = None

FONT_FAMILY='DejaVu Sans'
font = ''
def get_font():
    global font
    if font != '':
        return font
    if fontconfig:
        #fontconfig implementation is bad.
        fonts = fontconfig.query( family=FONT_FAMILY)
        fonts = [ fonts[i] for i in xrange( len( fonts)) ]
        for font in fonts:
            for lang,fullname in font.fullname:
                if fullname == FONT_FAMILY:
                    font = PIL.ImageFont.truetype( font.file, 14, encoding='unic')
                    return font
    font=PIL.ImageFont.load_default()

def make_image(text,format):
    if PIL is None:
        if format != 'png':
            raise ValueError, 'Errors image are generated in png only'
        return open( get_shared('icons/error.png'), 'rb')


    text = textwrap.wrap( text, width=WIDTH/8)
    dejavu = get_font()

    image = PIL.Image.new('RGB', ( WIDTH, 18*len( text) + 2 ), '#003499' )
    canvas = PIL.ImageDraw.Draw( image)
    for offset, line in enumerate( text):
        canvas.text((0, offset* 18 + 2 ), line, fill='#ffffff', font=dejavu)

    out = StringIO()
    image.save( out, format)
    out.seek(0)
    return out
