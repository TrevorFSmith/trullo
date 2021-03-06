var trullo = trullo || {};
trullo.views = trullo.views || {};

trullo.views.IndexView = Backbone.View.extend({
	className: 'routeView front-index-view',
	initialize: function(){
		_.bindAll(this);
		this.logEntries = new schema.LogEntryCollection([], {limit: 10, filters:{'source_url__isnull':true, 'publish':true, 'log__public':true}});
		this.logEntriesView = new publish.views.LogEntryCollectionView({showContent: true, title: 'Writin\'', collection:this.logEntries});
		this.logEntriesView.$el.addClass('span6');
		this.logEntries.fetch();

		this.streamEntries = new schema.LogEntryCollection([], {limit: 30, filters:{'source_url__isnull':'False'}});
		this.streamView = new publish.views.LogEntryCollectionView({title: 'Linkin\'', collection:this.streamEntries});
		this.streamView.$el.addClass('front-index-stream-view');
		this.streamView.$el.addClass('span6');
		this.streamEntries.on('add', this.handleStreamEntriesChange);
		this.streamEntries.on('reset', this.handleStreamEntriesChange);
		this.streamEntries.fetch();
	},
	handleStreamEntriesChange: function(){
		this.streamView.$el.find('ul').addClass('thumbnails');
		this.streamView.$el.find('.log-entry-item-view').addClass('thumbnail').addClass('span4');
	},
	render: function(){
		this.$el.empty();
		var row1 = $.el.div({class:'row-fluid'});
		this.$el.append(row1);
		row1.append(this.logEntriesView.render().el);
		row1.append(this.streamView.render().el);
		return this;
	},
});

trullo.views.AboutView = Backbone.View.extend({
	class: 'routeView',
	initialize: function(){
		_.bindAll(this, 'render');
		this.$el.addClass('aboutView');
		this.collection = new schema.UserCollection({filter:{'is_staff':true}});
		this.collection.bind('reset', this.render);
		this.collection.fetch();
	},
	render: function(){
		this.$el.empty();
		if(this.collection.length == 0) return this;
		user = this.collection.at(0);
		profile = user.get('profile');

		if(profile){
			var converter = new Markdown.Converter();
			this.$el.html(converter.makeHtml(profile.about));
		}
		return this;
	},
});

trullo.views.ContactView = Backbone.View.extend({
	class: 'routeView',
	initialize: function(){
		_.bindAll(this, 'render');
		this.$el.addClass('contactView');
		this.collection = new schema.UserCollection({filter:{'is_staff':true}});
		this.collection.bind('reset', this.render);
		this.collection.fetch();
	},
	render: function(){
		this.$el.empty();
		if(this.collection.length == 0) return this;
		user = this.collection.at(0);
		profile = user.get('profile');

		if(profile){
			var converter = new Markdown.Converter();
			this.$el.html(converter.makeHtml(profile.contact));
		}
		return this;
	},
});

trullo.views.JobItemView = Backbone.View.extend({
	className:'job-item-view',
	tagName:'li',
	initialize: function(){
		_.bindAll(this);
		this.$el.append($.el.h4(this.model.get('title')));		
		this.$el.append($.el.div({'class':'description'}, this.model.get('description')));
		var startDate = schema.parseJsonDate(this.model.get('started'));
		var dateRange = $.timeago(startDate) + ' - ';
		var ended = this.model.get('ended');
		if(ended){
			var endDate = schema.parseJsonDate(ended);
			dateRange += $.timeago(endDate);
		} else {
			dateRange += 'present';
		}	
		this.$el.append($.el.div({'class':'date-range'}, dateRange));
	}
});

trullo.views.JobGroupView = Backbone.View.extend({
	className:'job-group-view',
	initialize: function(){
		_.bindAll(this);
		this.$el.append($.el.h3(this.model.get('title')));
		this.jobItemViews = [];
		this.jobItemsUL = $.el.ul();
		this.$el.append(this.jobItemsUL);
		var jobsData = this.model.get('jobs');
		for(var i=0; i < jobsData.length; i++){
			var jobItemView = new trullo.views.JobItemView({'model':new Backbone.Model(jobsData[i])});
			this.jobItemViews[this.jobItemViews.length] = jobItemView;
			this.jobItemsUL.append(jobItemView.el);
		}
	}
});

trullo.views.JobsView = Backbone.View.extend({
	className: 'routeView job-view',
	initialize: function(){
		_.bindAll(this);
		this.collection = new schema.JobgroupCollection();
		this.collection.fetch({'success':this.initialRender});
	},
	initialRender: function(){
		this.groupViews = [];
		for(var i=0; i < this.collection.length; i++){
			var groupView = new trullo.views.JobGroupView({'model':this.collection.at(i)});
			this.groupViews[this.groupViews.length] = groupView;
			this.$el.append(groupView.el);
		}
	}
});
