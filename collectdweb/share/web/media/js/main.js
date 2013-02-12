/*jshint browser: true */

define([
       'jQuery',
       'utils',
       'hosts',
       'menu',
       'status',
       'grid'
], function( $, utils, HostsView, MenuTabs, StatusBar, GridView) {
    "use strict";

    var MainView = function() {
        this.effects = new utils.EffectsView();
        this.menu = new MenuTabs();
        this.ruler = new utils.Ruler();
        this.status = new StatusBar();
        this.error = new utils.ErrorView();
        this.grid = new GridView();
        this.hosts = new HostsView();

        this.menu.options.on('change-grid-view', this.grid.setView, this.grid);
        this.menu.options.on('set-ruler', this.toggleRuler, this);
        this.menu.options.on('set-lazy', this.grid.setLazy, this.grid);

        this.status.on( 'error', this.error.gotError, this.error);
        this.status.on( 'set-dates', this.grid.setDates, this.grid);
        this.status.on( 'change-timespan', this.grid.setTimespan, this.grid);

        this.status.on( 'select-all', this.grid.selectAll, this.grid);
        this.status.on( 'select-none', this.grid.selectNone, this.grid);

        this.status.on( 'move-all-forward', this.grid.moveAllForward, this.grid);
        this.status.on( 'move-all-backward', this.grid.moveAllBackward, this.grid);
        this.status.on( 'zoom-all-in', this.grid.zoomAllIn, this.grid);
        this.status.on( 'zoom-all-out', this.grid.zoomAllOut, this.grid);

        this.hosts.on( 'show-graphes', this.grid.displayGraphes, this.grid);
    };
    MainView.prototype.toggleRuler = function( showRuler ){
        if ( showRuler) {
            this.ruler.show();
        } else {
            this.ruler.hide();
        }
    };

    $(document).ready(function() {
        var main = new MainView();
    });
});
