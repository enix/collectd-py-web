/*jshint browser: true */

define([
       'jQuery',
       'underscore',
       'display'
], function( $, _, Display) {
    "use strict";
    var defaults = {
        autostart:true,
        className: 'collectd-graph',
        attr: 'href',
        target :  '.graph-imgs-container'
    };
    var options = _.extend( {}, defaults, window.collectdPyWebOptions);
    var refresh = window.collectdPyWebRefresh = function() {
        var display = new Display();
        var urls = $('.' + options.className).map(function(i,e){
            return $(e).attr( options.attr);
        });

        $( options.target)
        .empty()
        .append( display.status.render().el)
        .append( display.grid.render().el);

        display.grid.displayGraphes( urls );
    };
    if ( options.autostart) {
        $(document).ready(refresh);
    }
});


