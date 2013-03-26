/*jshint browser: true */

define([
       'Backbone',
       'jQuery',
       'underscore',
       'display',
       'utils',
       'hosts'
], function( Backbone, $, _, Display, utils, HostsView ) {
    "use strict";

    var MainView = function() {
        Display.call( this);
        this.effects = new utils.EffectsView();
        this.hosts = new HostsView();
        this.grid.on( 'export', this.export_, this);
        this.grid.on( 'output', this.output, this);
        this.hosts.on( 'show-graphes', this.grid.displayGraphes, this.grid);
    };
    _.extend( MainView.prototype, Display.prototype);
    MainView.prototype.export_ = function( urls ) {
        Backbone.ajax({
            type: 'post',
            url : '/sign/',
            data: _.map( urls, function( url) {
                return { name: 'url', value: url };
            })
        }).done( function(signatures) {
            var dialog = new utils.ExportDialog({ urls : signatures });
            $('body').append(dialog.render().el);
        }.bind(this));
    };
    MainView.prototype.output = function( url ) {
        var dialog = new utils.OutputDialog({ url : url });
        $('body').append(dialog.render().el);
    };

    $(document).ready(function() {
        var main = new MainView();
        $('#sidebar').append( main.hosts.render().el);
        $('#content')
        .append( main.status.render().el)
        .append( main.grid.render().el);
    });
});
