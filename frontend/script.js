//note: GLOBAL!! Required elsewhere
searched = []; //this will record any combination of search phrases and topics

function post(api, json, onResponse) {
  d3.json("http://localhost:5000/"+api+"/")
    .header("Content-Type", "application/json")
    .post(JSON.stringify(json), onResponse);
}

function ready() {
	//set up d3 visualization pane
	d3.select("#input-topic").on("keydown", function() {
	  var e = d3.event;
	  if (e.which === 13 || e.which === 10) {
	    e.preventDefault();
		var searchPhrase = d3.select(this).text();
	    addSearchPhrase(searchPhrase);
	  }
	}).on("click", function() {
	  return d3.select(this).text("");
	});

	//set up message panel
	setupMessagePanel();
}

function clearSearchBar() {
	d3.select("#input-topic").text("");
}

function resetSearchBar() {
	d3.select("#input-topic").text("Enter a topic...");
}

function removeTopicCallback(elem) {
	console.log("removing: ");
	console.log(elem);
	var parent = elem.parentElement;
	var text = parent.getElementsByClassName("searched-topic-text")[0].innerHTML;
	console.log(text);
	searched.splice(searched.indexOf(text),1);
	parent.parentElement.removeChild(parent);
	onSearchChanged();
}

function updateSearchedTopics() {
	var searchedTopics = d3.select('#searched-container').selectAll('.searched-topic-container')
		.data(searched);
	var s = searchedTopics.enter()
		.append('div')
		.attr('class','searched-topic-container');
	s
		.append('div')
		.attr('class', 'searched-topic-text')
		.text(function(d) {return d;});
	s
		.append('div')
		.attr('class', 'remove-search-topic')
		.attr('onclick', 'removeTopicCallback(this)');
	
	searchedTopics.exit().remove();
}

function onSearchChanged() {
	//new topic is pushed onto searched, so is last item
	//unless it's empty, then clear everything
	if (searched.length == 0) {
		clearMessagePanel();
		clearVisualization();
		resetSearchBar();
	} else {
		clearSearchBar();
		newVisualization(searched, addSearchTopic);
		updateMessagesPanel(searched);
	}
	updateSearchedTopics();
}


//**following two are separated out for later**

//text phrase, not necessarily a topic
function addSearchPhrase(newSearchPhrase) {
	console.log("adding new search phrase");
	searched.push(newSearchPhrase);
	console.log(searched);
	onSearchChanged();
}

//necessarily valid topic
function addSearchTopic(newSearchTopic) {
	console.log("adding new search topic " +  newSearchTopic.topic);
	searched.push(newSearchTopic.topic);
	console.log(searched);
	onSearchChanged();
}




