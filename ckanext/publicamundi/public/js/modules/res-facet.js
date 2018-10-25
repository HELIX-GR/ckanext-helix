this.ckan.module('res-facet', {

  initialize: function () {
    console.log('Ive been called for element');
    //var checkBoxState = localStorage.getItem('checkboxes');
    var form = $("#main-form-search");
    if ($("#main-form-search").length === 0){
      var form = $("#advanced-form-search");
    }
    else {
      var form = $("#main-form-search");
    }
    var checkboxes = $('.res-size');
    //var checkboxes = document.querySelectorAll('input[type=checkbox]')

    //console.log('Value is %s', checkboxes[0].checked);
    var checkBoxState;
    var checkbox = this.el[0];
    checkBoxState = localStorage.getItem(checkbox.value);
    console.log('checkbox: %s, state is: %s, value: %s', checkbox, checkBoxState, checkbox.value);


    if (checkBoxState === 'true') {
      $('<input type="hidden" id="ext_minsize" name="ext_minsize" value="" />').appendTo(form);
      //$('<input type="hidden" id="ext_minsize" name="ext_minsize" value="" />').appendTo(home_form);
      $('<input type="hidden" id="ext_maxsize" name="ext_maxsize" value="" />').appendTo(form);
     // $('<input type="hidden" id="ext_maxsize" name="ext_maxsize" value="" />').appendTo(home_form);


      if (checkbox.value == 1) {
        $('#ext_minsize').val('1');
        $('#ext_maxsize').val('1048576');
        checkbox.checked = true;
      } else if (checkbox.value == 10) {
        $('#ext_minsize').val('1048577');
        $('#ext_maxsize').val('10485760');
        checkbox.checked = true;
      } else if (checkbox.value == 100) {
        $('#ext_minsize').val('10485761');
        $('#ext_maxsize').val('104857600');
        checkbox.checked = true;
      } else if (checkbox.value == 1000) {
        $('#ext_minsize').val('104857601');
        $('#ext_maxsize').val('1048576000');
        checkbox.checked = true;
      }
    }
    else if (checkBoxState === 'false'){
      checkbox.checked = false;
    }

    $(".res-size").change(function () {

      localStorage.setItem(this.value, this.checked);
      console.log('val %s, checked %s', this.value, this.checked )
      if (this.checked) {
        
        if ($("#ext_minsize").length === 0) {
          $('<input type="hidden" id="ext_minsize" name="ext_minsize" value="" />').appendTo(form);
         // $('<input type="hidden" id="ext_minsize" name="ext_minsize" value="" />').appendTo(home_form);
        }
        if ($("#ext_maxsize").length === 0) {
          $('<input type="hidden" id="ext_maxsize" name="ext_maxsize" value="" />').appendTo(form);
          //$('<input type="hidden" id="ext_maxsize" name="ext_maxsize" value="" />').appendTo(home_form);
        }

        if ($(this).val() == 1) {
          $('#ext_minsize').val('1');
          $('#ext_maxsize').val('1048576');
        } else if ($(this).val() == 10) {
          $('#ext_minsize').val('1048577');
          $('#ext_maxsize').val('10485760');
        } else if ($(this).val() == 100) {
          $('#ext_minsize').val('10485761');
          $('#ext_maxsize').val('104857600');
        } else {
          $('#ext_minsize').val('104857601');
          $('#ext_maxsize').val('1048576000');
        }

        $("#main-form-search").submit();
      } else {
        $('#ext_minsize').remove();
        $('#ext_maxsize').remove();
        $("#main-form-search").submit();
      }

    });

  }

});