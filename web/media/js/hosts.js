define([
       'Backbone',
       'underscore',
       'jQuery',
       'Mustache'
], function( Backbone, _, $, Mustache) {
    "use strict";
    var getUrlPairs = function( list ) {
        return _.map( list.sort(), function(url) {
            return {
                url: url,
                name: _.chain( url.split('/')).compact().last().value()
            };
        });
    };
    var HostsView = Backbone.View.extend({
        template : Mustache.compile(
            '{{#hosts}}' +
            '<li>' +
            '<a href="{{url}}">{{ name }}</a>' +
            '</li>' +
            '{{/hosts}}'
        ),
        events: {
            'keyup #host-filter' : 'filter',
            'click a': 'selectHost'
        },
        initialize: function() {
            this.setElement('#hosts');
            this.plugins = new PluginsView();

            this.plugins.on( 'got-graphes', this.gotGraphes, this);

            Backbone.ajax({
                url : '/hosts/'
            }).done( this.gotHosts.bind( this));
        },
        gotHosts: function( hosts ) {
            this.$('ul').empty().append( this.template({ hosts : getUrlPairs( hosts) }));
        },
        filter: function(ev) {
            var target = $(ev.currentTarget);
            var search = target.val();
            if ( search === '') {
                this.$('li').show();
            } else {
                this.$('li').each(function(i,e) {
                    var element = $(e);
                    if ( element.text().toLowerCase().indexOf( search) === -1) {
                        element.hide();
                    } else {
                        element.show();
                    }
                });
            }
            target.focus();
            return true;
        },
        selectHost: function( ev) {
            this.$('a').removeClass('selected');

            var target = $(ev.currentTarget);
            target.addClass('selected');
            var host = target.attr('href');
            this.host = host;

            this.plugins.listHost( host);
            return false;
        },
        gotGraphes: function(graphes) {
            this.trigger( 'show-graphes', graphes);
        }
    });
    var PluginsView = Backbone.View.extend({
        initialize: function() {
            this.setElement("#plugins");
        },
        events: {
            'click ul li a': 'selectPlugin'
        },
        template: Mustache.compile(
            '<div>' +
            '<div class="ui-widget-header ui-corner-top"><h3>Available Plugins</h3></div>' +
            '<div id="plugin-container" class="ui-widget-content ui-corner-bottom  ">' +
            '<ul>{{#plugins}}' +
            '<li><a href="{{url}}" >{{name}}</a></li>' +
            '{{/plugins}}</ul>' +
            '</div>' +
            '</div>'
        ),
        listHost: function( host ){
            Backbone.ajax({
                url: host,
                data: {
                    group:'-'
                }
            }).done( this.gotPlugins.bind( this));
        },
        gotPlugins: function( plugins ) {
            this.$el.empty().append( this.template({ plugins: getUrlPairs( plugins) }));
        },
        selectPlugin: function(ev) {
            var target = $(ev.currentTarget);
            this.$('a').removeClass('selected');
            target.addClass('selected');

            var url = target.attr('href');
            Backbone.ajax({
                url : url
            }).done( this.gotGraphes.bind(this));
            return false;
        },
        gotGraphes: function( graphes ) {
            this.trigger('got-graphes', graphes);
        }
    });
    return HostsView;
});
