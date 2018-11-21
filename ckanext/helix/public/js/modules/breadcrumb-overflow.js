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
            
            var first_breadcrumb = $('.breadcrumbs-part:first');
            var txt3 = document.createElement("a");   // Create with DOM
            txt3.className = "breadcrumbs-part";
            txt3.innerHTML = " ...";
            if (bread_items>1){
                first_breadcrumb.after(txt3);
            }
            

            var toolbar = $('.breadcrumbs');
            toolbar.on('mouseenter', function () {
                bread_items.each(function () {
                    //console.log($(this).context.innerText);
                    //$(this).context.innerText = "...";
                    $(this).removeClass('hide-overflow');
                    //addClass('breadcrumb-hide-text');
                });
                txt3.className = "breadcrumbs-part hide-overflow";
            });

            toolbar.on('mouseleave', function () {
                bread_items.each(function () {
                    //console.log($(this).context.innerText);
                    //$(this).context.innerText = "...";
                    $(this).addClass('hide-overflow');
                    //addClass('breadcrumb-hide-text');
                });
                txt3.className = "breadcrumbs-part";
            });


        },

        teardown: function () {
            debug('Tearing down module: breadcrumb-overflow')
        },
    }
});