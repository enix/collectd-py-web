define([
       'status',
       'grid'
], function( StatusBar, GridView) {
    "use strict";
    var Display = function() {
        this.status = new StatusBar();
        this.grid = new GridView();

        this.status.on( 'set-dates', this.grid.setDates, this.grid);
        this.status.on( 'change-timespan', this.grid.setTimespan, this.grid);

        this.status.on( 'select-all', this.grid.selectAll, this.grid);
        this.status.on( 'select-none', this.grid.selectNone, this.grid);

        this.status.on( 'move-all-forward', this.grid.moveAllForward, this.grid);
        this.status.on( 'move-all-backward', this.grid.moveAllBackward, this.grid);
        this.status.on( 'zoom-all-in', this.grid.zoomAllIn, this.grid);
        this.status.on( 'zoom-all-out', this.grid.zoomAllOut, this.grid);
    };
    return Display;
});
