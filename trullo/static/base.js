var trullo = trullo || {};
trullo.views = trullo.views || {};

// Parse the variables out of the document's URL parameters
$.urlVars = function(){
	var vars = [], hash;
	var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
	for(var i = 0; i < hashes.length; i++) {
		hash = hashes[i].split('=');
		vars.push(hash[0]);
		vars[hash[0]] = unescape(hash[1]);
	}
	return vars;
};

// Get a specific variables out of the document's URL parameters
$.urlVar = function(name){
	return $.urlVars()[name];
};

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// This is used by the jQuery XHR to make requests.
trullo.CSRF_TOKEN = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// Set up the jQuery ajax requests to use the CSRF_TOKEN
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", trullo.CSRF_TOKEN);
        }
    }
});

trullo.browserCanEdit = function(){
	if(typeof window.FileReader == 'undefined'){
		return false;
	}
	return true;
}

/*
	options:
		collection: a Backbone.Collection
		itemView: the Backbone.View which will be used to present an item in the list
		title (optional): if present, add an H1 to the top of this list
		filter (optional): a boolean function which is passed an item from the collection and returns true if the item should be displayed
		mustBeSet (optional): an array of field names which must be present in an item in order for it to be displayed
		itemClasses (optional): a string which will be used for new items.$el.addClass
		click (optional): a callback for when an item generates a click event,
		draggable (optional): a dictionary of options to pass when calling jQueryUI's $.draggable on each view in the collection
*/
trullo.views.AbstractCollectionView = Backbone.View.extend({
	tagName: 'section',
	initialize: function(options){
		this.options = options;
		_.bindAll(this, 'reset', 'add', 'remove', 'indexOf');
		this.$el.addClass('collection-view');
		this.itemViews = [];
		this.itemList = $.el.div({'class':'item-list'});

		if(this.options.title){
			this.$el.append($.el.h1(this.options.title));
		}
		this.$el.append(this.itemList);

		if(this.options.sortable){
			$(this.itemList).sortable(this.options.sortable);
		}

		if(this.options.emptyEl){
			this.emptyMessage = $.el.div({'class':'empty-collection-view-message'}).appendTo(this.el);
			$(this.emptyMessage).append(this.options.emptyEl);
		}

		this.reset();
		this.listenTo(this.collection, 'add', this.add);
		this.listenTo(this.collection, 'remove', this.remove);
		this.listenTo(this.collection, 'reset', this.reset);
	},
	indexOf: function(itemView){
		var itemEls = $(this.itemList).find('.item-view');
		for(var i=0; i < itemEls.length; i++){
			var dataItem = $(itemEls[i]).data('itemView');
			if(itemView.cid == dataItem.cid){
				return i;
			}
		}
		return -1;
	},
	reset: function(){
		for(var i=0; i < this.itemList.length; i++){
			this.itemList[i].remove();
		}
		$(this.itemList).empty()
		for(var i=0; i < this.collection.length; i++){
			this.add(this.collection.at(i));
		}
		if(this.options.sortable){
			$(this.itemList).sortable(this.options.sortable);
		}
		if(this.emptyMessage){
			$(this.emptyMessage).toggle(this.collection.length == 0);
		}
	},
	add: function(item){
		if(this.options.filter){
			if(!this.options.filter(item)){
				return;
			}
		}
		if(this.options.mustBeSet){
			for(var i=0; i < this.options.mustBeSet.length; i++){
				var val = item.get(this.options.mustBeSet[i], null);
				if(val == null || val == '') return;
			}
		}

		var newView = new this.options.itemView({'model':item, 'parentView':this, 'parent':this.collection});
		this.itemViews[this.itemViews.length] = newView;
		newView.$el.addClass('item-view');
		newView.$el.data('itemView', newView);
		if(this.options.itemClasses){
			newView.$el.addClass(this.options.itemClasses);
		}
		this.itemList.appendChild(newView.render().el);
		if(this.options.click){
			newView.$el.click(function(){
				this.view.options.click(this.itemView.model);
			}.bind({
				'view':this,
				'itemView': newView
			}));
		}

		if(this.emptyMessage){
			$(this.emptyMessage).toggle(this.collection.length == 0);
		}
	},
	remove: function(item){
		for(var i=0; i < this.itemViews.length; i++){
			if(item.id == this.itemViews[i].model.id){
				this.itemViews[i].remove();
				if(this.options.click){
					this.itemViews[i].off('click');
				}
				this.itemViews = _.without(this.itemViews, this.itemViews[i]);
				return;
			}
		}
		if(this.emptyMessage){
			$(this.emptyMessage).toggle(this.collection.length == 0);
		}
	}
});

/*
	options:
		titleText: optional text for this modal, defaults to nothing
		body: the DOM element that should be shown as the main content of the modal
		okCallback: an optional callback function for when the ok button is selected
		hideOnOk: defaults to true, if false the modal will not hide and remove itself upon selection of the ok button
		okText: the optional button text for the primary action button, defaults to "OK"
		okBTNClass: the optional bootstrap btn class for the ok button, defaults to "btn-primary"
		cancelText: the optional button text for the cancel button, defaults to "Cancel"
*/
trullo.views.GenericModal = Backbone.View.extend({
	className: 'generic-modal modal',
	events: {
		'click .cancel-button': 'handleCancel',
		'click .ok-button': 'handleOk',
	},
	initialize: function(options){
		_.bindAll(this, 'show', 'handleShown', 'handleHidden', 'handleCancel', 'handleOk');
		this.options = options;
		if(_.isUndefined(this.options.hideOnOk)){
			this.options.hideOnOk = true;
		}

		this.$el.attr('role', 'dialog');
		this.$el.attr('tabindex', '-1');

		this.oked = false;

		this.dialog = $.el.div({'class':'modal-dialog', 'role':'document'}).appendTo(this.el);
		
		this.content = $.el.div({'class':'modal-content', 'aria-labelledby':'generic-modal-title'}).appendTo(this.dialog);
		
		this.header = $.el.div({'class':'modal-header'}).appendTo(this.content);
		this.closeButton = $.el.button({'type':'button', 'class':'close', 'data-dismiss':'modal', 'aria-label':'Close'}).appendTo(this.header);
		this.closeSpan = $.el.span({'aria-hidden':'true'}).appendTo(this.closeButton);
		$(this.closeSpan).html('&times');
		this.title = $.el.h4({'class':'modal-title', 'id':'generic-modal-title'}, this.options.titleText || '').appendTo(this.header);

		this.body = $.el.div({'class':'modal-body'}).appendTo(this.content);
		this.body.appendChild(this.options.body);

		this.footer = $.el.div({'class':'modal-footer'}).appendTo(this.content);
		this.cancelButton = $.el.button({'type':'button', 'class':'btn btn-default cancel-button'}, $.el.span({'class':'glyphicon glyphicon-remove'}), this.options.cancelText || ' Cancel').appendTo(this.footer);
		if(this.options.okBTNClass){
			var okBTNClass = this.options.okBTNClass;
		} else {
			var okBTNClass = 'btn-primary';
		}
		this.saveButton = $.el.button({'type':'button', 'class':'btn ' + okBTNClass + ' ok-button'}, this.options.okText || 'OK').appendTo(this.footer);

		this.$el.on('show.bs.modal', this.handleShown);
		this.$el.on('hide.bs.modal', this.handleHidden);
	},
	handleCancel: function(){
		this.$el.modal('hide');
	},
	handleOk: function(){
		if(this.oked) return;
		this.oked = true;
		if(this.options.okCallback){
			this.options.okCallback(this);
		}
		if(this.options.hideOnOk){
			this.$el.modal('hide');
		}
	},
	handleShown: function(){
		// Override if needed
	},
	handleHidden: function(){
		this.remove();
	},
	show: function(){
		this.$el.modal({
			'show': true
		});
	}
});

// Set the input to the field value and then update the field when input changes
trullo.views.bindInput = function(model, field, targetEl){
	var $targetEl = $(targetEl);
	$targetEl.text(model.get(field) || '');
	$targetEl.keyup(function(e){
		model.set(field, $targetEl.val());
	});
}

// Set the targetEl's text to whatever is in the field as it changes
trullo.views.bindText = function(model, field, targetEl){
	var $targetEl = $(targetEl);
	$targetEl.text(model.get(field));
	model.on('change:' + field, function(){
		$targetEl.text(model.get(field));
	});
}

// Set the targetEl's attribute to the value of the field as it changes
trullo.views.bindAttribute = function(model, field, targetEl, attribute){
	var $targetEl = $(targetEl);
	$targetEl.attr(attribute, model.get(field));
	model.on('change:' + field, function(){
		$targetEl.attr(attribute, model.get(field));
	});
}
