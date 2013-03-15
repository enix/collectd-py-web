
.PHONY: docs

all: sdist

sdist: js
	python setup.py sdist

js: optimized extern

optimized:
	r.js -o web/setup.js

extern:
	r.js -o web/extern.json


docs:
	make -C docs html

clean:
	-rm -r collectd_py_web.egg-info _build build MANIFEST.in collectdweb/share/web/
	make -C docs clean

mrproper: clean
	rm -rf dist/*
