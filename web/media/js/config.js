/*jshint strict: false */
var require = {
    paths: {
        'text' : 'libs/require-text',
        'jQuery' : 'libs/jquery',
        'Backbone' : 'libs/backbone',
        'Mustache' : 'libs/mustache',
        'underscore' : 'libs/underscore',
        'jQuery-ui': 'libs/jquery-ui'
    },
    baseUrl: '/media/js',
    shim: {
        'Backbone' : {
            exports : 'Backbone',
            deps : [ 'underscore', 'jQuery' ],
            init : function( _, $) {
                this.Backbone.$ = $;
                return this.Backbone.noConflict();
            }
        },
        'libs/bootstrap/modals' : [ 'jQuery' ],
        'underscore' : {
            'exports' : '_',
            init: function() {
                return this._.noConflict();
            }
        },
        jQuery: {
            'exports' : '$'
            /*init: function() {
                return this.$.noConflict();
            }*/
        },
        'jQuery-ui': [ 'jQuery' ]
    }
};
