this.ckan.module('res-facet', function (jQuery) {
    return {
      initialize: function () {
        console.log('Ive been called for element');

        var form = $("#main-form-search");
        var home_form = $("#advanced-form-search");

        $(".res-size").change(function() {
              if(this.checked) {
                if ($("#ext_minsize").length === 0) {
                  $('<input type="hidden" id="ext_minsize" name="ext_minsize" value="" />').appendTo(form);
                  $('<input type="hidden" id="ext_minsize" name="ext_minsize" value="" />').appendTo(home_form);
                }
                if ($("#ext_maxsize").length === 0) {
                  $('<input type="hidden" id="ext_maxsize" name="ext_maxsize" value="" />').appendTo(form);
                  $('<input type="hidden" id="ext_maxsize" name="ext_maxsize" value="" />').appendTo(home_form);
                }
                //var search_form = document.getElementById("main-form-search");
                //var search_text = document.getElementById("landing-search-text");
                //search_text.value= search_text.value +  "res_size\:[1 TO 7400]";
                //console.log('In input search is %s', search_text.value);
                //search_form.submit();

                //var url = window.location.href;  
                //url = url + "&res_size\:[1 TO 7400]";
                //console.log('Url is %s', url);
                //window.location.href = url;
                //console.log('value is %s', $(this).val() );
                if ($(this).val() == 1){
                  $('#ext_minsize').val('1');
                  $('#ext_maxsize').val('1048576');
                }
                else if ($(this).val() == 10){
                  $('#ext_minsize').val('1048577');
                  $('#ext_maxsize').val('10485760');
                }
                else if ($(this).val() == 100){
                  $('#ext_minsize').val('10485761');
                  $('#ext_maxsize').val('104857600');
                }
                else {
                  $('#ext_minsize').val('104857601');
                  $('#ext_maxsize').val('1048576000');
                }
                
                $("#main-form-search").submit();
              }
              
          });

      }
    };
  });
