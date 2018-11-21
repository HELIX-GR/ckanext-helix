this.ckan.module('order-by', function (jQuery) {
    return {
      initialize: function () {
        //console.log('Ive been called for element');

        $("select").change(function() {
              var search_form = document.getElementById("main-form-search");
              search_form.submit();
          });

      }
    };
  });
