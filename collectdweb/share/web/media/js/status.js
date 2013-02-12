
define([
       'Backbone',
       'jQuery'
], function( Backbone, $) {
    "use strict";
    var StatusBar = Backbone.View.extend({
        events: {
            'click #select-all': 'selectAll',
            'click #select-none' : 'selectNone',
            'click #rrdeditor-submit' : 'submitDate',
            'click .ui-icon-home' : 'showHome',
            'click #item-pan-zoom' : 'showPanZoom',
            'click #item-timespan' : 'showTimespan',
            'click .ts-item': 'selectTimespan',
            'click .ui-icon-triangle-1-e': 'moveAllForward',
            'click .ui-icon-triangle-1-w': 'moveAllBackward',
            'click .ui-icon-zoomin': 'zoomInAll',
            'click .ui-icon-zoomout': 'zoomOutAll'
        },
        initialize: function(){
            this.setElement('#toolbar-content');
        },
        selectAll: function() {
            this.trigger( 'select-all');
            return false;
        },
        selectNone: function() {
            this.trigger( 'select-none');
            return false;
        },
        moveAllForward: function() {
            this.trigger( 'move-all-forward');
            return false;
        },
        moveAllBackward: function() {
            this.trigger( 'move-all-backward');
            return false;
        },
        zoomOutAll: function() {
            this.trigger( 'zoom-all-out');
            return false;
        },
        zoomInAll: function() {
            this.trigger( 'zoom-all-in');
            return false;
        },
        submitDate: function(){
            var start = Date.parse(this.$('.timespan-from').val());
            var end = Date.parse( this.$('.timespan-to').val());

            if (!start || !end) {
                this.trigger('error', 'One of the dates is invalid');
            } else {
                this.trigger('set-dates', start, end);
            }
            return false;
        },
        _showItem : function( item ) {
            this.$('.toolbar-item').not(item).fadeOut();
            this.$(item).fadeIn();
        },
        showHome: function() {
            this._showItem( '.menu-options');
            return false;
        },
        showTimespan: function() {
            this._showItem( '.item-timespan');
            return false;
        },
        showPanZoom: function() {
            this._showItem( '.item-pan-zoom');
            return false;
        },
        selectTimespan: function(ev) {
            var target = $(ev.currentTarget);
            var timespan = target.attr('title');
            this.trigger( 'change-timespan', timespan);
        }
    });
    return StatusBar;
});
