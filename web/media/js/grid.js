/*jshint browser: true */

define([
       'Backbone',
       'underscore',
       'jQuery',
       'addtime',
       'graphview'
], function( Backbone, _, $, addTime, GraphView) {
    "use strict";
    var GridView = Backbone.View.extend({
        tagName : 'ul',
        initialize: function() {
            this.selected = [];
        },
        output: function( view) {
            this.trigger('output', view.getImgSrc());
        },
        export_: function( view) {
            var views = this._getSelected( view);
            var urls = _.map( views, function( view) {
                return view.getImgSrc();
            });
            this.trigger('export', urls);
        },
        setView: function( view ) {
            if ( view === 'grid') {
                this.$el.addClass('view-grid');
            } else {
                this.$el.removeClass('view-grid');
            }
        },
        setDates: function( start, end) {
            _.each( this.views, function( view){
                view.setDates( start, end);
            });
        },
        setTimespan: function( timespan) {
            var end = new Date();
            var start = addTime( end, -1, timespan);

            _.each( this.views, function( view){
                view.setDates( start, end);
            });
        },
        _getSelected: function( view ) {
            if ( this.selected.length ) {
                return this.selected;
            } else if ( view ) {
                return [ view ];
            } else {
                return this.views;
            }
        },
        moveAllForward: function() {
            _.map( this._getSelected(), function(x) {
                x.moveForward();
            });
        },
        moveAllBackward: function() {
            _.map( this._getSelected(), function(x) {
                x.moveBackward();
            });
        },
        zoomAllIn: function() {
            _.map( this._getSelected(), function(x) {
                x.zoomIn();
            });
        },
        zoomAllOut: function() {
            _.map( this._getSelected(), function(x) {
                x.zoomOut();
            });
        },
        selectAll: function( ){
            this.selected = _.map( this.views, function( v) {
                v.setSelected( true);
                return v;
            });
        },
        selectNone: function() {
            _.map( this.views, function( v) {
                v.setSelected( false);
            });
            this.selected = [];
        },
        select: function( view) {
            var isSelected = _.contains( this.selected, view);
            view.setSelected( !isSelected);
            if ( isSelected ) {
                this.selected = _.without( this.selected, view);
            } else {
                this.selected.push(view);
            }
        },
        displayGraphes: function( graphes) {
            var end = new Date();
            var start = addTime( end, -1, 'day');

            this.views = _.map( graphes, function( url ) {
                var view = new GraphView({
                    lazy: this._lazyIsSet,
                    url : url,
                    start: start,
                    end: end
                });
                view.on( 'select', this.select, this);
                view.on( 'output', this.output, this);
                view.on( 'export', this.export_, this);
                return view;
            }, this);
            this.$el.empty().append(_.map( this.views, function(v) {
                return v.render().el;
            }));
        },
        setLazy: function( isSet ) {
            if ( isSet === this._lazyIsSet) {
                return ;
            }
            this._lazyIsSet = isSet;
            if ( isSet) {
                $(window).on( 'scroll', this._lazyCheck.bind(this));
            } else {
                $(window).off( 'scroll', this._lazyCheck );
            }
        },
        _lazyCheck: function(){
            var windowTop = $(window).height() + $(window).scrollTop();
            _.chain( this.view).filter(function(x) {
                return x.lazy;
            }).each( function(x) {
                x.checkLazy(windowTop);
            });
        }
    });
    return GridView;
});
