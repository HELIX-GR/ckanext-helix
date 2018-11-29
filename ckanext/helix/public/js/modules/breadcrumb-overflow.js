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
            bread_items.each(function () {
                //console.log($(this).context.innerText);
                //$(this).innerHTML = "...";
                $(this).addClass('hide-overflow');
            });
            
            var first_breadcrumb = $('.breadcrumbs-part:first');
            if (bread_items.length > 0)
                var txt = document.createElement("a");   // Create with DOM
                var dots = document.createTextNode("...");
                txt.appendChild(dots);
                txt.className = "breadcrumbs-part";
                first_breadcrumb.after(txt);
            
            

            var toolbar = $('.breadcrumbs');
            toolbar.on('mouseenter', function () {
                bread_items.each(function () {
                    //console.log($(this).context.innerText);
                    //$(this).context.innerText = "...";
                    $(this).removeClass('hide-overflow');
                    //addClass('breadcrumb-hide-text');
                });
                txt.className = "breadcrumbs-part hide-overflow";
            });

            toolbar.on('mouseleave', function () {
                bread_items.each(function () {
                    //console.log($(this).context.innerText);
                    //$(this).context.innerText = "...";
                    $(this).addClass('hide-overflow');
                    //addClass('breadcrumb-hide-text');
                });
                txt.className = "breadcrumbs-part";
            });


        },

        teardown: function () {
            debug('Tearing down module: breadcrumb-overflow')
        },
    }
});