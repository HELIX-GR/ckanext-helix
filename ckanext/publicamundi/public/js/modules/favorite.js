/* Follow buttons
 * Handles calling the API to follow the current user
 *
 * action - This being the action that the button should perform. Currently: "favorite" or "unfavorite"
 * type - The being the type of object the user is trying to support. Currently: "user", "group" or "dataset"
 * id - id of the objec the user is trying to follow
 * loading - State management helper
 *
 * Examples
 *
 *   <a data-module="follow" data-module-action="follow" data-module-type="user" data-module-id="{user_id}">Follow User</a>
 *
 */
this.ckan.module('favorite', function($) {
	return {
		/* options object can be extended using data-module-* attributes */
		options : {
            action: null,
			email: null,
			name: null,
			title: null,
            notes: null,
            loading: false
		},

		/* Initialises the module setting up elements and event listeners.
		 *
		 * Returns nothing.
		 */
		initialize: function () {
			$.proxyAll(this, /_on/);
			this.el.on('click', this._onClick);
		},

		/* Handles the clicking of the favorite button
		 *
		 * event - An event object.
		 *
		 * Returns nothing.
		 */
		_onClick: function(event) {
			var options = this.options;
			if (
				options.action
				&& options.email
				&& options.name
                && options.title
                && !options.loading
			) {
				event.preventDefault();
				var client = this.sandbox.client;
				var path = options.action;
				options.loading = true;
				this.el.addClass('disabled');
                client.call('POST', path, { email : options.email, name : options.name, title : options.title, notes : options.notes   }, this._onClickLoaded);
                
			}
		},

		/* Fired after the call to the API to either follow or unfollow
		 *
		 * json - The return json from the follow / unfollow API call
		 *
		 * Returns nothing.
		 */
		_onClickLoaded: function(json) {
			var options = this.options;
			var sandbox = this.sandbox;
			var oldAction = options.action;
			options.loading = false;
			
			//if (options.action == 'favorite') {
				
			//} else {
			
			//}
		}
	};
});
