this.ckan.module('closed-tags-module', function ($, _) {
  return {
    options: {
      dataset: ''
    }
    initialize: function () {
      console.log('this dataset is: %s', this.options.dataset);
      this.select2({
        theme: "bootstrap",
		placeholder: "Select a State",
			maximumSelectionSize: 6,
			  containerCssClass: ':all:'
			  });
      //=> "this dataset is: my dataset"
    }
  }
});

