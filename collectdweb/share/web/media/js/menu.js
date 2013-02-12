define([
       'Backbone',
       'jQuery',
       'Mustache'
], function( Backbone, $, Mustache) {
    "use strict";
    var MenuTabs = Backbone.View.extend({
        events : {
            'click #slide-menu-btn': 'slide'
        },
        initialize: function() {
            this.setElement( '#slide-menu-container');
            this.$('#menu-tabs').tabs();
            this.options = new OptionsTab();
        },
        slide: function(ev) {
            this.$('#slide-menu-content').slideToggle('fast');
            $(ev.currentTarget).toggleClass('active');
            return false;
        }
    });
    var OptionsTab = Backbone.View.extend({
        events : {
            'click #show-ruler-checkbox': 'toggleRuler',
            'change #graph-view' : 'changeGridView',
            'click #graph-caching-checkbox': 'toggleLazy'
        },
        initialize: function() {
            this.setElement('#options-tab');
        },
        toggleRuler: function(ev) {
            var target = $(ev.currentTarget);
            this.trigger( 'set-ruler', target.prop('checked') );
        },
        toggleLazy: function( ev) {
            var target = $(ev.currentTarget);
            this.trigger( 'set-lazy', target.prop('checked') );
        },
        changeGridView: function( ev) {
            var target = $(ev.currentTarget);
            this.trigger( 'change-grid-view', target.val());
        }
    });
    return MenuTabs;
});
