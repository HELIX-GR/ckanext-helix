this.ckan.module('request-resource', function ($) {
    return {
        /* options object can be extended using data-module-* attributes */
        options: {
            action: null,
            contact_email: null,
        },

		/* Initialises the module setting up elements and event listeners.
		 *
		 * Returns nothing.
		 */
        initialize: function () {
            $.proxyAll(this, /_on/);
            this.el.on('click', this._onClick);
            var request_btn = document.getElementById('btnRequest');
        },

		/* Handles the clicking of the request button
		 *
		 * event - An event object.
		 *
		 * Returns nothing.
		 */
        _onClick: function (event) {
            console.log('in onclick');
            var options = this.options;
            var btn_request = document.getElementById('btnRequest');
            btn_request.disabled = false;
            $('#result-text').html('');
            var options = this.options;
            var defaults = {
                top: 100,
                overlay: 0.5,
                closeButton: "#modal_close"
            }

            var overlay = $("<div id='lean_overlay'></div>");

            $("body").append(overlay);


            var o = defaults;


            var modal_id = "#modal-request";

            $("#lean_overlay").click(function () {
                $("#lean_overlay").fadeOut(200);
                $(modal_id).css({
                    'display': 'none'
                });
            });

            $(o.closeButton).click(function () {
                $("#lean_overlay").fadeOut(200);
                $(modal_id).css({
                    'display': 'none'
                });

            });

            var modal_height = $(modal_id).outerHeight();
            var modal_width = $(modal_id).outerWidth();

            $('#lean_overlay').css({
                'display': 'block',
                opacity: 0
            });

            $('#lean_overlay').fadeTo(200, o.overlay);

            $(modal_id).css({

                'display': 'block',
                'opacity': 0,
                'z-index': 11000,

            });

            $(modal_id).fadeTo(200, 1);

            var client = this.sandbox.client;
            var result_text = document.getElementById('result-text');
            function _onClickLoaded(json) {
                $('#result-text').html(json.result);
                if (json.result == 'Mail sent!') {
                    btn_request.disabled = true;
                    result_text.style.color = '#333';
                }
                else {
                    result_text.style.color = 'red';
                }

            };
            $(btn_request).click(function (event) {
                event.preventDefault();
                var form = document.getElementById('request_form');
                //validate form
                var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
                if (form.email.value == '' || form.message.value == "" || !(re.test(String(form.email.value)))) {
                    $(result_text).html('Please fill all fields correctly');
                    result_text.style.color = 'red';
                    return;
                }
                client.call('POST', 'request_resource', {
                    email: form.email.value, message: form.message.value, package_name: options.package_name,
                    creator_id: options.creator_id, resource_id: options.resource_id, resource_name: options.resource_name,
                    pkg_title: options.pkg_title, contact_email: options.contact_email
                }, _onClickLoaded);

            });
        }
    };
});