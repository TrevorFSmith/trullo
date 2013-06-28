
var schema = schema || {};

schema.initialCap = function(str){
	return str.substring(0, 1).toUpperCase() + str.substring(1)
}

schema.javascriptifyResourceName = function(resourceName){
	var result = schema.initialCap(resourceName);
	while(result.indexOf('-') != -1){
		var index = result.indexOf('-');
		result = result.substring(0, index) + schema.initialCap(result.substring(index + 1));
	}
	return result;
}

schema.hostNameFromURL = function(url){
	var splitURL = url.split('/');
	return splitURL[2];
}

schema.getCookie = function(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

schema.apiSync = function(method, model, options){
	var new_options =  _.extend({
		beforeSend: function(xhr) {
			xhr.setRequestHeader("X-CSRFToken", schema.getCookie('csrftoken'));
		}
	}, options);
	Backbone.sync(method, model, new_options);
}

schema.AbstractTastyPieModel = Backbone.Model.extend({
	url: function(){
		if(typeof this.get('id') == 'undefined') return this.list_endpoint;
		return this.list_endpoint + this.get('id');
	},

	schemaUrl: function(){
		return this.list_endpoint + 'schema';
	},
});
schema.AbstractTastyPieModel.prototype.sync = schema.apiSync;

schema.AbstractTastyPieCollection = Backbone.Collection.extend({
	initialize: function(models, options){
		_.bindAll(this, 'url', 'pageUp', 'pageDown', 'page');
		this.options = options || {};
		this.limit = this.options.limit ? parseInt(this.options.limit) : 50;
		this.offset = this.options.offset ? parseInt(this.options.offset) : 0;
	},
	pageUp: function(){ this.page(-1); },
	pageDown: function(){ this.page(1); },
	page: function(delta){
		this.offset = this.offset + (delta * this.limit);
		if(this.offset < 0) this.offset = 0;
		this.fetch();
	},
	url: function(){
		result = this.list_endpoint + '?';
		result = result + 'limit=' + this.limit;
		if(this.offset > 0){
			result = result + '&offset=' + this.offset;
		}
		if(this.options.filters){
			for(var name in this.options.filters){
				result = result + '&' + name + '=' + this.options.filters[name];
			}
		}
		return result;
	}, 
});
schema.AbstractTastyPieCollection.prototype.sync = schema.apiSync;

schema.TastyPieSchema = Backbone.Model.extend({
	url: '/api/v0.1/',
	populate: function(){
		for(var name in this.attributes){
			var resourceClassName = schema.javascriptifyResourceName(name);
			schema[resourceClassName] = schema.AbstractTastyPieModel.extend({
				list_endpoint: this.attributes[name].list_endpoint,
			});
			schema[resourceClassName + 'Collection'] = schema.AbstractTastyPieCollection.extend({
				list_endpoint: this.attributes[name].list_endpoint,
				model: schema[resourceClassName],
			});
		}
		this.trigger('populated', this);
	}
});

schema.tastyPieSchema = new schema.TastyPieSchema();

$(document).ready(function(){
	schema.tastyPieSchema.fetch({success: function(){
		schema.tastyPieSchema.populate();
	}});
});

schema.parseJsonDate = function(jsonDate){
	var dateString = jsonDate.split('T')[0];
	var dateArray = dateString.split('-');
	var date = new Date(dateArray[1] + ' ' + dateArray[2] + ' ' + dateArray[0]);
	if(jsonDate.split('T').length > 1){
		var timeArray = jsonDate.split('T')[1].split(':');
	} else {
		var timeArray = ['0', '0', '0'];
	}
	return new Date(date.getFullYear(), date.getMonth(), date.getDate(), parseInt(timeArray[0], 10), parseInt(timeArray[1], 10), parseInt(timeArray[2], 10));
}

schema.formatDate = function(jsDate){
	return schema.MONTH_STRINGS[jsDate.getMonth()] + ' ' + jsDate.getDate() + ', ' + jsDate.getFullYear();
}

schema.MONTH_STRINGS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

var views = views || {};

views.truncateWords = function(text, length){
	// Returns as many as `length` words from `text`
	if(!text) return text;
	if(!length || length === 0) return '';

	var textArray = text.split(/\s+/);
	if(length < textArray.length) {
		return textArray.slice(0, length).join(' ') + ' ...';
	}
	return text;
}

views.AbstractCollectionView = Backbone.View.extend({
	tagName: 'section',
	initialize: function(){
		_.bindAll(this, 'render', 'add', 'remove', 'reset');
		this.$el.addClass('collection-view');
		this.itemViews = [];
		this.itemList = $.el.ul();

		this.collection.on('add', this.add);
		this.collection.on('remove', this.remove);
		this.collection.on('reset', this.reset);
	},
	reset: function(){
		this.render();
		for(var i=0; i < this.collection.length; i++){
			this.add(this.collection.at(i));
		}
	},
	add: function(item){
		if(this.options.filter){
			var filterName = this.options.filter[0];
			var filterTargetValue = this.options.filter[1];
			var val = item.get(filterName, null);
			if(val != filterTargetValue) return;
		}
		if(this.options.mustBeSet){
			for(var i=0; i < this.options.mustBeSet.length; i++){
				var val = item.get(this.options.mustBeSet[i], null);
				if(val == null || val == '') return;
			}
		}
		this.itemViews[this.itemViews.length] = new this.itemView({model:item, parentView:this});
		this.itemList.append(this.itemViews[this.itemViews.length - 1].render().el);
	},
	remove: function(idea){
		console.log('remove', arguments);
	},
	render: function(){
		this.$el.empty();
		$(this.itemList).empty()
		if(this.options.title) this.$el.append($.el.h1(this.options.title));
		this.$el.append(this.itemList);
		return this;
	},
})

views.AbstractItemView = Backbone.View.extend({
	tagName: 'li',
	initialize: function(){
		_.bindAll(this, 'render');
		this.$el.addClass('item-view');
		if(this.options.additionalClasses){
			for(var i=0; i < this.options.additionalClasses.length; i++){
				this.$el.addClass(this.options.additionalClasses);
			}
		}
	},
});

views.TastyPieModelForm = Backbone.View.extend({
	/*
	This view displays a form for a given Backbone.Model.
	It relies on the metadata provided at the model's schemaUrl method.

	Options:
		model: the model of interest
		showFirst: array of field name strings in the order which they should be displayed
	*/
	tagName: 'form',
	className: 'model-form',
	initialize: function(){
		_.bindAll(this, 'render', 'handleChange', 'handleInput', 'handleSubmit', 'validate');
		this.$el.attr('action', '.');
		this.$el.attr('method', 'post');
		this.fieldOrder = null;
		this.schemaInitialized = false;
		this.isValid = false;

		if(this.options.modelSchema){
			this.modelSchema = this.options.modelSchema;
		} else {
			var model = Backbone.Model.extend({
				url: this.model.schemaUrl(),
			});
			this.modelSchema = new model();
			this.modelSchema.fetch();
		}
		this.modelSchema.on('change', this.handleChange);
		this.$el.submit(this.handleSubmit);
	},

	handleChange: function(){
		if(this.schemaInitialized) return;
		this.schemaInitialized = true;

		var fields = this.modelSchema.get('fields')
		this.fieldOrder = [];
		// First, add any field names in showFirst
		if(this.options.showFirst){
			for(var i=0; i < this.options.showFirst.length; i++){
				if(fields[this.options.showFirst[i]]) this.fieldOrder[this.fieldOrder.length] = this.options.showFirst[i];
			}
		} 
		// Then, add the rest of the field names
		for(var name in fields){
			if($.inArray(name, this.fieldOrder) != -1) continue; // Already added via showFirst
			this.fieldOrder[this.fieldOrder.length] = name;
		}
		this.render();
		this.validate();
	},

	validate: function(){
		var validated = true;
		var inputs = this.$el.find('input');
		for(var i=0; i < inputs.length; i++){
			var fieldInfo = $.data(inputs[i], 'backbone-field');
			switch(fieldInfo['field']['type']){
				case 'string':
				case 'integer':
					if(this.model.get(fieldInfo['name'])){
						$(inputs[i]).removeClass('invalid-input');
					} else {
						$(inputs[i]).addClass('invalid-input');
						validated = false;
					}
					break;
				case 'boolean':
					break;
				default:
					// pass
			}
		}
		this.isValid = validated;
		this.$el.find('button[type=submit]').attr('disabled', this.isValid ? null : 'disabled');
	},

	handleInput: function(event){
		var fieldInfo = $.data(event.target, 'backbone-field');
		var name = fieldInfo['name'];
		switch(fieldInfo['field']['type']){
			case 'string':
			case 'integer':
				this.model.set(name, $(event.target).val());
				break;
			case 'boolean':
				ths.model.set(name, $(event.target).attr('checked') == 'checked');
				break;
			default:
				console.log("Unhandled field info type", fieldInfo['field']['type']);
		}
		this.validate();
	},

	handleSubmit: function(){
		this.model.save(null, {
			success: _.bind(function(model, xhr, options){
				this.render();
				if(this.options.savedCallback) this.options.savedCallback(this.model);
			}, this),
			error: _.bind(function(model, xhr, options){
				this.render();
			}, this)
		});
		return false;
	},

	render: function(){
		this.$el.empty()
		if(this.fieldOrder == null) return this;

		var fields = this.modelSchema.get('fields');
		for(var i in this.fieldOrder){
			var name = this.fieldOrder[i]
			var field = fields[name];

			if(name == 'id') continue; 
			if(field['readonly']) continue;

			var label = $.el.label({class:'model-form-label model-form-' + field['type'] + '-label'}, name);
			this.$el.append(label);

			var input = null;
			switch(field['type']){
				case 'integer':
					var input = $.el.input({type:'text', class:'model-form-integer-input', value: this.model.get(name)});
					$(input).keyup(this.handleInput);
					this.$el.append(input);
					break;
				case 'string':
					var input = $.el.input({type:'text', class:'model-form-string-input', value: this.model.get(name)});
					$(input).keyup(this.handleInput);
					this.$el.append(input);
					break;
				case 'boolean':
					var input = $.el.input({type:'checkbox', class:'model-form-boolean-input'});
					this.$el.append(input);
					if(field['default'] == true) $(input).attr('checked', 'checked');
					$(input).change(this.handleInput);
					break;
			}
			if(input){
				$.data(input, 'backbone-field', {'model':this.model, 'name':name, 'field':field});
			}
		}

		this.submitButton = $.el.button({type:'submit'}, this.model.id ? 'Update' : 'Create');
		this.$el.append(this.submitButton);
		return this;
	},
})

/*
Copyright 2012 Trevor F. Smith (http://trevor.smith.name/) 
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/