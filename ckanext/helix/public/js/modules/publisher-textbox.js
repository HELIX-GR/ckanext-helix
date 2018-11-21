this.ckan.module('publisher-textbox', function ($, _) {
  
    var debug = $.proxy(window.console, 'debug')
    var warn = $.proxy(window.console, 'warn')
    
    return {
  
      
      
      initialize: function() 
      {
          var module = this,
              $el = this.el,
              qname = $el.attr('name')
              
          var text = $select.find("option:selected").text();  
          
          if (el.value=="0"){
                $other.show()
  
          } 
  
          debug('Initialized module: input-select-choices')
      },
      
      teardown: function() 
      { 
          debug('Tearing down module: input-select-choices')
      },
    }
});
