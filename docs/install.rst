============
Installation
============


Dependencies
============

Collectdweb needs a few dependencies to run.

Requirements
------------

It requires Bottle, a popular web micro framework.

Collectdweb use the binary version of rrdtool (and not the python C extension).
If the rrdtool binary is not in $PATH, adjust :data:`~collectdweb.settings.RRDTOOL_BIN`.

Gevent is recommended in order to run the rrdtool subprocesses without blocking the web server.
The version of Gevent required is at least the 1.0

Optional
--------

When an error is encountered in the process of generating an image,
Collectdweb will try to catch the exception and print the text in an image,
so that the browser can display it.

This feature requires PIL and fontconfig.


Deployement
===========

1) Initialize a new virtual env::

       $ virtualenv collectdweb
       $ source collectdweb/bin/activate

2) Gevent is not yet released in its 1.0 version.
   You may need to retrieve it from the dev repos.

   Gevent needs Cython and the python-dev packages.::

       # apt-get install python-dev

       $ pip install cython
       $ pip install git+git://github.com/SiteSupport/gevent.git 

3) Get an archive of collectdweb and install it::

   $ pip install collectd-py-web-1.0.tar.gz

4) Run it::

   $ collectdweb


Use a wgsi server
-----------------

Collectdweb follow the wsgi conventions and expose a variable :data:`~collectdweb.wsgi.application` in  
the :mod:`collectdweb.wsgi`.

.. note::

   Importing :mod:`collectdweb.wsgi` will call :func:`gevent.monkey.patch_all`, as it is needed by bottle.

Custom settings
---------------

If you need to run collectdweb with custom settings, follow the step 1 and 2
and instead of installing the archive, extract it.
Create a local module :mod:`localsettings.py<collectdweb.localsettings>` inside collectdweb and override the settings in it::

    collectdweb/localsettings.py

    RRDTOOL_BIN='/opt/collectd/bin/rrdtool'


Javascript and medias
=====================

The javascripts and CSS needed by the web interface are optimized by r.js.
In order to build the scripts, you need Node and r.js
The scripts are build by::

    make js


