(function(window){
    var _times = {
        minute: 60,
        hour: 60*60,
        day: 24*60*60,
        week: 7*24*60*60,
        month: 31*24*60*60,
        year: 365.25*24*60*60
    };
    var addTime = function( date, interval, timespan) {
        if ( _.isUndefined( timespan)) {
            return new Date( date.getTime() + interval);
        } else {
            return new Date( date.getTime() + interval * 1000 * _times[timespan] );
        }
    };
    var GraphView = Backbone.View.extend({
        tagName : 'li',
        className : 'gc',
        events: {
            'click .ui-icon-triangle-1-w' : 'moveBackward',
            'click .ui-icon-triangle-1-e' : 'moveForward',
            'click .ui-icon-zoomin': 'zoomIn',
            'click .ui-icon-zoomout': 'zoomOut',
            'click .ui-icon-close' : 'close',
            'click .ui-icon-star' : 'toggleSelected',
            'click .ui-icon-disk' : 'output',
            'click .ui-icon-bookmark' : 'exportLink' 
        },
        initialize : function( opts ) {
            this.lazy = opts.lazy;
            this.src = opts.url;
            this.end = opts.end || new Date();
            this.start = opts.start || addTime( this.end, -1, 'hour');
        },
        template: Mustache.compile(
            '<span class="gc-menu fg-toolbar ui-widget-header ui-corner-all ui-helper-clearfix" >' +
            '<span class="icons ui-state-default ui-corner-all"><span class="ui-icon ui-icon-triangle-1-w"></span></span>' +
            '<span class="icons ui-state-default ui-corner-all"><span class="ui-icon ui-icon-triangle-1-e"></span></span>' +
            '<span class="icons ui-state-default ui-corner-all"><span class="ui-icon ui-icon-zoomin"></span></span>' +
            '<span class="icons ui-state-default ui-corner-all"><span class="ui-icon ui-icon-zoomout"></span></span>' +
            '<span class="icons ui-state-default ui-corner-all"><span class="ui-icon ui-icon-disk"></span> </span>' +
            '<span class="icons ui-state-default ui-corner-all"><span class="ui-icon ui-icon-star"></span></span>' +
            '<span class="icons ui-state-default ui-corner-all"><span class="ui-icon ui-icon-close"></span></span>' +
            '<span class="icons ui-state-default ui-corner-all"><span class="ui-icon ui-icon-bookmark"></span></span>' +
            '</span>' +
            '<span class="selectable"></span>' +
            '<img class="gc-img" src="{{ url }}" title="{{url}}" />'
        ),
        render: function(){
            this.$el.append( this.template({
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
                    '&end=' + this._getFormated( this.end ));
        },
        toggleSelected: function() {
            this.trigger( 'select', this);
        },
        setSelected: function( selected ) {
            if ( selected ) {
                this.$('.selectable').addClass('selected');
            } else {
                this.$('.selectable').removeClass('selected');
            }
        },
        close: function(){
            this.trigger( 'destroy');
            this.remove();
        },
        output: function() {
            this.trigger( 'export', this);
        },
        exportLink: function() {
            this.trigger( 'export-link', this);
        },
        checkLazy: function( windowTop) {
            var elemTop = this.$el.offset().top;
            if ((windowTop > elemTop) && (elemTop !== 0)) {
                this.lazy = false;
                this._update();
            }
        }
    });
    window.addTime = addTime;
    window.GraphView = GraphView;
})(this);
