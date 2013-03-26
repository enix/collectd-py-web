
define([
       'Backbone',
       'jQuery',
       'text!templates/status.html'
], function( Backbone, $, template) {
    "use strict";
    var StatusBar = Backbone.View.extend({
        tagName: 'div',
        id:'graph-toolbar',
        className:'btn-toolbar home',
        events: {
            'click .select-all': 'selectAll',
            'click .select-none' : 'selectNone',
            'click .menu-timespn' : 'submitDate',
            'click .home' : 'showHome',
            'click .pan-zoom' : 'showPanZoom',
            'click .timespn' : 'showTimespan',
            'click .year': 'selectTimespanYear',
            'click .month': 'selectTimespanMonth',
            'click .week': 'selectTimespanWeek',
            'click .day': 'selectTimespanDay',
            'click .hour': 'selectTimespanHour',
            'click .forward': 'moveAllForward',
            'click .backward': 'moveAllBackward',
            'click .zoomin': 'zoomInAll',
            'click .zoomout': 'zoomOutAll'
        },
        render: function() {
            this.$el.append( template);
            this.$('.menu-options').hide();
            this.$('.menu-timespn').hide();
            return this;
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
            this.$('.menu-options, .menu-timespn, .menu-pan-zoom').not(item).fadeOut();
            this.$(item).fadeIn();
        },
        showHome: function() {
            this._showItem( '.menu-options');
            return false;
        },
        showTimespan: function() {
            this._showItem( '.menu-timespn');
            return false;
        },
        showPanZoom: function() {
            this._showItem( '.menu-pan-zoom');
            return false;
        },
        selectTimespanHour: function(ev) {
            this.trigger( 'change-timespan', 'hour');
        },
        selectTimespanDay: function(ev) {
            this.trigger( 'change-timespan', 'day');
        },
        selectTimespanMonth: function(ev) {
            this.trigger( 'change-timespan', 'month');
        },
        selectTimespanWeek: function(ev) {
            this.trigger( 'change-timespan', 'week');
        },
        selectTimespanYear: function(ev) {
            this.trigger( 'change-timespan', 'year');
        }
    });
    return StatusBar;
});
