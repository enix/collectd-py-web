/*jshint browser: true */
define([
       'Backbone',
       'jQuery',
       'Mustache',
       'jQuery-ui'
], function( Backbone, $, Mustache) {
    "use strict";
    var LoadingIndicator = Backbone.View.extend({
        initialize: function() {
            this.setElement('#loading');
            this.$el
            .ajaxStart( this.show.bind(this))
            .ajaxStop( this.hide.bind(this));
        },
        show : function() {
            this.$el.show();
        },
        hide: function() {
            this.$el.hide();
        }
    });
    var Ruler = Backbone.View.extend({
        initialize: function() {
            this.setElement('#ruler');
            this.$el.draggable({
                axis: 'x'
            });
        },
        show: function() {
            this.$el.fadeIn();
        },
        hide: function() {
            this.$el.fadeOut();
        }
    });
    var EffectsView = Backbone.View.extend({
        events : {
            'mouseenter .icons' : 'addHoverEffect',
            'mouseleave .icons' : 'dropHoverEffect'
        },
        initialize: function() {
            this.setElement( 'body');
            this.$('button').button();
            if( navigator.platform === 'iPad' ||
               navigator.platform === 'iPhone' ||
                   navigator.platform === 'iPod') {
                this.ipadWorkArround();
            }
        },
        dropHoverEffect: function( ev) {
            $(ev.currentTarget).removeClass('ui-state-hover');
        },
        addHoverEffect: function( ev) {
            $(ev.currentTarget).addClass('ui-state-hover');
        },
        ipadWorkArround: function() {
            $( window ).scroll( function () {
                $( "#toolbar-container" ).css(
                    "top", ( $( window ).height() + $( document ).scrollTop() - 30 ) +"px"
                );
            });
        }
    });
    var ErrorView = Backbone.View.extend({
        initialize: function() {
            this.setElement('#error-msg');
            this.$el.dialog({
                modal:true,
                autoOpen:false,
                resizable:false,
                draggable:false,
                title: 'An error has ocurred',
                //open: this.open.bind( this),
                buttons:{
                    Ok: this.close.bind( this)
                }
            });
        },
        close: function() {
            this.$el.dialog('close');
        },
        gotError: function( error) {
            this.$('.content').html( error);
            this.$el.dialog('open');
        }
    });
    var ExportDialog = Backbone.View.extend({
        initialize: function() {
            this.setElement('#exports-dialog');
            this.$el.dialog({
                title : 'Exportable urls of the graphes',
                modal : true,
                autoOpen: false
            }).parent().css('z-index', '50');
        },
        template: Mustache.compile(
            '<pre>{{#urls}}' +
            '{{.}}\n'+
            '{{/urls}}</pre>' +
            '<div>{{#urls}}' +
            '<input type="text" value="{{.}}" /><br />' +
            '{{/urls}}</div>'
        ),
        launch: function(urls) {
            this.$('.content').empty().append( this.template({ urls: urls }));
            this.$el.dialog('open');
        }
    });
    var OutputDialog = Backbone.View.extend({
        initialize: function() {
            this.setElement('#output-dialog');
            this.$el.dialog( {
                title : 'Select output format:',
                modal : true,
                autoOpen: false
            });
        },
        launch: function(url) {
            var linker = url.indexOf('?') !== -1 ? '&' : '?';
            this.$('.output-link').each( function( i, e){
                var $e = $(e);
                var newUrl = url + linker + 'format=' + $e.attr('title');
                $e.attr('href', newUrl);
            });
            this.$el.dialog('open');
        }
    });
    return {
        'Ruler': Ruler,
        'ErrorView' : ErrorView,
        'OutputDialog' : OutputDialog,
        'ExportDialog' : ExportDialog,
        'EffectsView' : EffectsView,
        'LoadingIndicator' : LoadingIndicator
    };
});
