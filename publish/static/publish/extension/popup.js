browser.tabs.query({currentWindow: true, active: true}).then(activeTab => {
	browser.tabs.get(activeTab[0].id).then(tabInfo => {
		document.getElementById('id_url').value = tabInfo.url
		document.getElementById('id_title').value = tabInfo.title
	})
})
