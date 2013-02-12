

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

clean:
	@echo no no i clean
