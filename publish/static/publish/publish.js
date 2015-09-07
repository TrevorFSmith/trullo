var publish = publish || {};
publish.views = publish.views || {};

publish.createMailtoURL = function(toAddress, subject, body){
	var result = 'mailto:';
	if(toAddress) result += toAddress;
	if(subject || body) result += '?';
	if(subject) result += 'subject=' + escape(subject);
	if(body){
		if(subject) result += '&';
		result += 'body=' + escape(body);
	}
	return result;
}

publish.views.LogItemView = Backbone.View.extend({
	className: 'log-item-view',
	render: function(){
		this.$el.empty();
		var title = $.el.h3($.el.a({href:this.model.get('absolute_url')}, this.model.get('title')));
		this.$el.append(title);
		return this;
	},
});

publish.views.LogCollectionView = trullo.views.AbstractCollectionView.extend({
	className: 'log-collection-view',
	itemView: publish.views.LogItemView,
});

publish.views.IdeasView = Backbone.View.extend({
	className: 'idea-view row-fluid',
	initialize: function(){
		_.bindAll(this, 'render', 'handleFormSaved');

		this.ideaForm = new views.TastyPieModelForm({model: new schema.Idea(), showFirst:['title', 'description', 'public'], 'savedCallback':this.handleFormSaved});
		this.collectionView = new publish.views.IdeaCollectionView({showContent: true, title: 'Ideas', collection:this.collection});
		this.collectionView.$el.addClass('span9');
	},
	handleFormSaved: function(model){
		document.location.reload();
	},
	render: function(){
		this.$el.empty();

		if(!this.options.hideForm){
			var row1 = $.el.div({class:'row-fluid'});
			this.$el.append(row1);
			row1.append(this.ideaForm.render().el);
		}

		var row2 = $.el.div({class:'row-fluid'});
		this.$el.append(row2);
		row2.append(this.collectionView.el);
	},
});

publish.views.LogView = Backbone.View.extend({
	className: 'log-view row-fluid',
	initialize: function(){
		_.bindAll(this, 'render', 'jobChanged');
		this.logEntriesView = null;
		this.model.bind('change', this.jobChanged);
	},
	jobChanged: function(){
		this.logEntries = new schema.LogEntryCollection([], {limit: 20, filters:{'log__slug':this.model.get('slug')}});
		this.logEntriesView = new publish.views.LogEntryCollectionView({showContent: true, title: this.model.get('title'), collection:this.logEntries});
		this.logEntriesView.$el.addClass('span9');
		this.render();
		this.logEntries.fetch();
	},
	render: function(){
		this.$el.empty();
		var row1 = $.el.div({class:'row-fluid'});
		this.$el.append(row1);
		if(this.logEntriesView){
			row1.append(this.logEntriesView.render().el);
		}
	},
});

publish.views.LogEntryView = Backbone.View.extend({
	className: 'log-entry-view',
	initialize: function(){
		_.bindAll(this, 'render');
		this.$el.addClass('log-entry-view');
		this.model.bind('change', this.render);
	},
	render: function(){
		this.$el.empty();
		this.$el.append($.el.h1(this.model.get('subject')));
		var photos = this.model.get('photos');
		var thumbnailsList = $.el.ul({'class':'thumbnails'});
		this.$el.append(thumbnailsList);
		for(var i=0; i < photos.length; i++){
			var span = thumbnailsList.append($.el.li({'class':'span4'}));
			console.log(photos[i]);
			var anchor = span.append($.el.a({'href':photos[i]['image'], 'target':'_new', 'class':'thumbnail'}));
			anchor.append($.el.img({'src':photos[i]['web_image_url']}))
		}

		var content = this.model.get('content');
		if(content){
			var converter = new Markdown.Converter();
			this.$el.append(converter.makeHtml(content));
		}
		return this;
	}
});

publish.views.LogEntryItemView = Backbone.View.extend({
	className: 'log-entry-item-view',
	render: function(){
		var subject = $.el.h3();
		this.$el.append(subject);
		var subjectAnchor = subject.append($.el.a({href:this.model.get('absolute_url')}, this.model.get('subject')));
		if(this.model.get('source_url', null)) subjectAnchor.setAttribute('rel', 'nofollow');
		if(this.model.get('source_url')){
			this.$el.append($.el.p(schema.hostNameFromURL(this.model.get('source_url'))));
		}
		if(this.options.parentView && this.options.parentView.options.showContent){
			var content = views.truncateWords(this.model.get('content'), 50);
			var converter = new Markdown.Converter();
			var convertedContent = converter.makeHtml(content);
			this.$el.append(convertedContent);
		}
		return this;
	},
});

publish.views.LogEntryCollectionView = trullo.views.AbstractCollectionView.extend({
	className: 'log-entry-collection-view',
	itemView: publish.views.LogEntryItemView,
});

publish.views.IdeaItemView = Backbone.View.extend({
	className: 'idea-item-view',
	render: function(){
		this.$el.empty();
		this.$el.append($('<h3>').html(this.model.get('title')));
		var converter = new Markdown.Converter();
		this.$el.append($('<p>').html(converter.makeHtml(this.model.get('description'))));
		return this;
	},
});

publish.views.IdeaCollectionView = trullo.views.AbstractCollectionView.extend({
	className: 'idea-collection-view',
	itemView: publish.views.IdeaItemView,
});

publish.views.ProjectItemView = Backbone.View.extend({
	className: 'project-item-view',
	render: function(){
		if(this.model.get('url')){
			var title = $.el.h3();
			this.$el.append(title);
			var anchor = title.append($.el.a({href:this.model.get('url')}));
			$(anchor).html(this.model.get('title'));
		} else {
			this.$el.append($('<h3 />').html(this.model.get('title')));
		}
		var description = $('<p />').html(this.model.get('description')); 
		this.$el.append(description);

		var metadata = $.el.div({'class':'metadata'});
		this.$el.append(metadata);
		var ended = this.model.get('ended');
		if(ended){
			var endDate = schema.parseJsonDate(ended);
			metadata.append($.el.span($.timeago(endDate)));
		} else {
			metadata.append($.el.span('ongoing'));
		}
		return this;
	},
});

publish.views.ProjectCollectionView = trullo.views.AbstractCollectionView.extend({
	className: 'project-collection-view',
	itemView: publish.views.ProjectItemView,
});

publish.views.ProjectsView = Backbone.View.extend({
	className: 'routeView',
	initialize: function(){
		_.bindAll(this, 'render');
		this.projectCollection = new schema.ProjectCollection({limit:1000});
		this.portfolioCollectionView = new publish.views.ProjectCollectionView({collection:this.projectCollection, filter:['portfolio', true]})
		this.portfolioCollectionView.$el.addClass('span6');
		this.projectCollectionView = new publish.views.ProjectCollectionView({collection:this.projectCollection, filter:['portfolio', false]})
		this.projectCollectionView.$el.addClass('span6');
		this.projectCollection.fetch();
	},
	render: function(){
		var row1 = $.el.div({class:'row-fluid'});
		this.$el.append(row1);
		row1.append(this.portfolioCollectionView.render().el);
		row1.append(this.projectCollectionView.render().el);
		return this;
	},
});

publish.views.PublicationItemView = Backbone.View.extend({
	className: 'publication-item-view',
	render: function(){
		this.$el.append($('<h3 />').html('"' + this.model.get('title') + '"'));
		this.$el.append($.el.p(this.model.get('authors'), '.'));
		var publicationDate = schema.parseJsonDate(this.model.get('publication_date'));
		this.$el.append($.el.p(this.model.get('venue'), '. ', schema.formatDate(publicationDate), '.'));
		if(this.model.get('document')){
			this.$el.append($.el.a({href:this.model.get('document')}, 'download'))
		}
		if(this.model.get('source_url')){
			this.$el.append($.el.a({href:this.model.get('source_url')}, 'source'))
		}
		return this;
	},
});

publish.views.PublicationCollectionView = trullo.views.AbstractCollectionView.extend({
	className: 'publication-collection-view',
	itemView: publish.views.PublicationItemView,
});

publish.views.PublicationsView = Backbone.View.extend({
	className: 'routeView',
	initialize: function(){
		_.bindAll(this, 'render');
		this.collection = new schema.PublicationCollection({limit:1000});
		this.collectionView = new publish.views.PublicationCollectionView({collection:this.collection});
		this.collectionView.$el.addClass('span12');
		this.collection.fetch();
	},
	render: function(){
		var row1 = $.el.div({class:'row-fluid'});
		this.$el.append(row1);
		row1.append(this.collectionView.render().el);
		return this;
	},
});
