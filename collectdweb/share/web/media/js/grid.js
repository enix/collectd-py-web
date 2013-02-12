/*jshint browser: true */

define([
       'Backbone',
       'underscore',
       'jQuery',
       'Mustache',
       'utils',
       'addtime',
       'graphview'
], function( Backbone, _, $, Mustache, utils, addTime, GraphView) {
    "use strict";
    var GridView = Backbone.View.extend({
        initialize: function() {
            this.setElement( '#graph-container');
            this.selected = [];
            this.outputDialog = new utils.OutputDialog();
            this.exportDialog = new utils.ExportDialog();
        },
        output: function( view ) {
            this.outputDialog.launch( view.getImgSrc());
        },
        exportLink: function( view) {
            var views = this._getSelected( view);
            Backbone.ajax({
                url : '/sign/',
                data: _.map( views, function( view) {
                    return { name: 'url', value: view.src };
                })
            }).done( function(signatures) {
                this.exportDialog.launch(signatures);
            }.bind(this));
        },
        setView: function( view ) {
            if ( view === 'grid') {
                this.$el.addClass('view-grid');
            } else {
                this.$el.removeClass('view-grid');
            }
        },
        template : Mustache.compile(
            '<li class="ui-widget graph-image">' +
            '<ul class="sortable ui-sortable" >' +
            '</ul>' +
            '</li>'
        ),
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

            var container = $('<ul>');
            var origin = location.protocol + '//' + location.host ;

            this.views = _.map( graphes, function( url ) {
                var view = new GraphView({
                    lazy: this._lazyIsSet,
                    url : origin + url,
                    start: start,
                    end: end
                });
                view.on( 'select', this.select, this);
                view.on( 'export', this.output, this);
                view.on( 'export-link', this.exportLink, this);
                container.append(view.render().el);
                return view;
            }, this);
            this.$el.empty().append( container);
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
