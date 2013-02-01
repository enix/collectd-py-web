/*jshint browser: true */
/*global Backbone: false, $: false, _:false, Mustache: false */

(function(window) {
    "use strict";
    var GraphView = window.GraphView;
    var defaults = {
        autostart:true,
        className: 'collectd-graph',
        attr: 'href'
    };
    var options = _.extend( {}, defaults, window.collectPyWebOptions);
    var refresh = window.collectdPyWebRefresh = function() {
        $('.' + options.className).each(function(i,e){
            var target = $(e);
            var src = target.attr(options.attr); 
            target.replaceWith( $('<ul>', {
                'className' : "graph-imgs-container"
            }).append( new GraphView({ url: src }).render().el));
        });
    };
    if ( options.autostart) {
        $(document).ready(refresh);
    }
})(this);
