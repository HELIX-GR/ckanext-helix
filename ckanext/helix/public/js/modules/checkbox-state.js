/* Finds the nearest select box in a form and watches it for changes. When
 * a change occurs it submits the form. It can also hide the submit button if
 * required.
 *
 * target - A selector to watch for changes (default: select)
 * button - A selector for the button to hide in the form.
 *
 * Examples
 *
 *   <form data-module="select-switch" data-module-target="">
 *    <label for="field-order">Sort By:</label>
 *    <select id="field-order"></select>
 *    <button type="submit">Go</button>
 *   </form>
 *
 * Returns .
 */
this.ckan.module('checkbox-state', {

    options: {
        target: 'select'
    },

    initialize: function () {
        var _this = this;
        console.log('IN CHECKBOX STATE')
        var checkboxValues = JSON.parse(localStorage.getItem('checkboxValues')) || {},
            $checkboxes = $("#checkbox-list :checkbox");

        $checkboxes.on("change", function () {
            $checkboxes.each(function () {
                checkboxValues[this.id] = this.checked;
            });

            localStorage.setItem("checkboxValues", JSON.stringify(checkboxValues));
        });

        // On page load
        $.each(checkboxValues, function (key, value) {
            $("#" + key).prop('checked', value);
        });
    }
});