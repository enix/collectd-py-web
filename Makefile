
.PHONY: docs

all: sdist

sdist: js
	python setup.py sdist

js: optimized collectd.js

optimized:
	r.js -o web/setup.js

collectd.js: optimized
	cat collectdweb/share/web/media/js/libs/require.js\
 	   	collectdweb/share/web/media/js/extern.js >\
 	   	collectdweb/share/web/media/js/collectd.js 

docs:
	make -C docs html

clean:
	-rm -r collectd_py_web.egg-info _build build MANIFEST.in collectdweb/share/web/
	make -C docs clean

mrproper: clean
	rm -rf dist/*
