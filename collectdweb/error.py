#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cStringIO import StringIO
import textwrap
from collectdweb import get_shared


"""

This module exports :func:`make_image` which generate an image
with some text inside in order to figure an error directly in the <img> tag.

It requires PIL to work but is not mandatory for collectdweb.

.. data:: WIDTH

    The width of the generated images.
    he height depends on the quantity of text.

.. data:: FONT_FAMILY

    The font family used to write on the images.
    this feature requires fontconfig in addition to PIL
"""

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

__all__ = [ 'make_image' ]

FONT_FAMILY='DejaVu Sans'
font = ''
def get_font():
    """
    Return a PIL font instance of the font used to write in images.
    This font is :data:`FONT_FAMILY` or the default font if it is unavailable.

    This font is memoized after the first call.
    """
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
    return font

def make_image(text,format):
    """
    Generate an image showing the given text.

    Used to show the error with the right content-type in a browser.
    A text response would be shown as an error.
    An image would be shown to the user so that he can understand what caused the error.

    :param format: The destination format of the error image.
    """
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
