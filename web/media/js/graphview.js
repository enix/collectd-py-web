define([
       'Backbone',
       'Mustache',
       'addtime',
       'text!templates/menu.html'
], function( Backbone, Mustache, addTime, menuTemplate) {
    "use strict";
    var GraphView = Backbone.View.extend({
        tagName : 'li',
        className : 'graph',
        events: {
            'click .backward' : 'moveBackward',
            'click .forward' : 'moveForward',
            'click .zoomin': 'zoomIn',
            'click .zoomout': 'zoomOut',
            'click .remove' : 'close',
            'click .select' : 'toggleSelected',
            'click .output' : 'output',
            'click .export' : 'export_',
            'click .upper-up': 'augmentUpper',
            'click .upper-down': 'reduceUpper'
        },
        initialize : function( opts ) {
            this.lazy = opts.lazy;
            this.src = opts.url;
            this.end = opts.end || new Date();
            this.start = opts.start || addTime( this.end, -1, 'hour');
            this.upper = null;
        },
        template: Mustache.compile(
            '<img class="graph-img" src="{{ url }}" title="{{url}}" />'
        ),
        render: function(){
            this.$el
            .append( menuTemplate)
            .append( this.template({
                url: this.lazy ? this.loadingUrl : this.getImgSrc()
            }));
            return this;
        },
        setDates: function( start, end){
            this.start = start;
            this.end = end;
            this._update();
        },
        _getFormated: function( date) {
            return ( date.getTime() / 1000).toFixed();
        },
        moveBackward: function() {
            this._move( -1);
        },
        moveForward: function() {
            this._move( 1);
        },
        zoomIn: function() {
            this._zoom( 1);
        },
        zoomOut: function() {
            this._zoom( -1);
        },
        augmentUpper: function() {
            this._upper( 1);
        },
        reduceUpper: function() {
            this._upper( -1);
        },
        _getInterval: function() {
            var start_millis = this.start.getTime();
            var end_millis = this.end.getTime();
            return end_millis - start_millis;
        },
        _move: function( direction) {
            var interval = this._getInterval();
            this.start = addTime( this.start, (direction * interval)/2 );
            this.end = addTime( this.end, (direction * interval) / 2);
            this._update();
        },
        _zoom: function( factor) {
            var zoom = 0.5 * factor * this._getInterval();
            this.start = addTime( this.start, zoom );
            this._update();
        },
        _upper: function( delta) {
            if ( this.upper === null ){
                this.upper = 10000;
            }
            this.upper += Math.ceil( this.upper * delta * (10 / 100));
            if ( Math.abs(this.upper - 10000) < 500) {
                this.upper = null;
            }
            this._update();
        },
        _update: function() {
            if ( this.lazy) {
                return ;
            }
            this.$('img').attr('src', this.getImgSrc());
        },
        getImgSrc: function() {
            var linker = this.src.indexOf('?') !== -1 ? '&' : '?';
            return ( this.src + linker +
                    'start=' + this._getFormated( this.start) +
                    '&end=' + this._getFormated( this.end ) +
                    ( this.upper !== null ? '&upper=' + (this.upper/100).toFixed() + '%' : '')
                   );
        },
        toggleSelected: function() {
            this.trigger( 'select', this);
        },
        setSelected: function( selected ) {
            if ( selected ) {
                this.$('.select').addClass('active');
                this.$el.addClass('selected');
            } else {
                this.$('.select').removeClass('active');
                this.$el.removeClass('selected');
            }
        },
        close: function(){
            this.trigger( 'destroy');
            this.remove();
        },
        output: function() {
            this.trigger( 'output', this);
        },
        export_: function() {
            this.trigger( 'export', this);
        },
        checkLazy: function( windowTop) {
            var elemTop = this.$el.offset().top;
            if ((windowTop > elemTop) && (elemTop !== 0)) {
                this.lazy = false;
                this._update();
            }
        }
    });
    return GraphView;
});
