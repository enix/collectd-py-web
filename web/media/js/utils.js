/*jshint browser: true */
define([
       'Backbone',
       'jQuery',
       'Mustache',
       'libs/bootstrap/modal',
       'text!templates/exports.html',
       'text!templates/output.html'
], function( Backbone, $, Mustache, $modal, exportsTemplate, outputTemplate) {
    "use strict";
    var EffectsView = Backbone.View.extend({
        initialize: function() {
            this.setElement( 'body');
            if( navigator.platform === 'iPad' ||
               navigator.platform === 'iPhone' ||
                   navigator.platform === 'iPod') {
                this.ipadWorkArround();
            }
        },
        ipadWorkArround: function() {
            $( window ).scroll( function () {
                $( "#toolbar-container" ).css(
                    "top", ( $( window ).height() + $( document ).scrollTop() - 30 ) +"px"
                );
            });
        }
    });
    var ExportDialog = Backbone.View.extend({
        className : 'modal hide fade',
        template: Mustache.compile(
            exportsTemplate
        ),
        initialize: function(options) {
            this.urls = options.urls;
        },
        render: function() {
            this.$el
            .append( this.template({ urls : this.urls }))
            .modal();
            return this;
        }
    });
    var OutputDialog = Backbone.View.extend({
        className : 'modal hide fade',
        template: Mustache.compile(
            outputTemplate
        ),
        initialize: function( options) {
            this.url = options.url;
        },
        render: function() {
            this.$el.append( this.template({
                url : this.url,
                link : this.url.indexOf('?') !== -1 ? '&' : '?'
            }))
            .modal();
            return this;
        }
    });
    return {
        'OutputDialog' : OutputDialog,
        'ExportDialog' : ExportDialog,
        'EffectsView' : EffectsView
    };
});
