/*
 * A module for select-based input for choices
 */
this.ckan.module('breadcrumb-overflow', function ($, _) {

    var debug = $.proxy(window.console, 'debug')
    var console = window.console


    return {

        options: {},

        initialize: function () {
            var $el = this.el            //Breadcrumbs auto hide all but last element
            var bread_items = $('.breadcrumbs-part:first').nextAll();
            bread_items = bread_items.not(':last');
            console.log(bread_items, "Hello, world!");
            bread_items.each(function () {
                //console.log($(this).context.innerText);
                //$(this).context.innerText = "...";
                console.log($(this), "Hello, world2");
                $(this).addClass('hide-overflow');
            });

            var toolbar = $('.breadcrumbs');
            toolbar.on('mouseenter', function () {
                bread_items.each(function () {
                    //console.log($(this).context.innerText);
                    //$(this).context.innerText = "...";
                    $(this).removeClass('hide-overflow');
                    //addClass('breadcrumb-hide-text');
                });
            });

            toolbar.on('mouseleave', function () {
                bread_items.each(function () {
                    //console.log($(this).context.innerText);
                    //$(this).context.innerText = "...";
                    $(this).addClass('hide-overflow');
                    //addClass('breadcrumb-hide-text');
                });
            });


        },

        teardown: function () {
            debug('Tearing down module: breadcrumb-overflow')
        },
    }
});