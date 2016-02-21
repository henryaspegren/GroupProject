

function callBackend(api, json, onResponse) {
  d3.json("http://localhost:5000/"+api+"/")
    .header("Content-Type", "application/json")
    .post(JSON.stringify(json), onResponse);
}

/* test data for visualizer */
var testSearchTopic = {topic : 'runescape', message_count : 200};

var testRelatedTopics = [
	{topic : 'inventions', message_count: 150},
	{topic : 'skills', message_count : 100},
	{topic : 'trump', message_count : 50},
	{topic : 'inventions', message_count: 10},
	{topic : 'skills', message_count : 30},
	{topic : 'trump', message_count : 80},
	{topic : 'inventions', message_count: 110},
	{topic : 'skills', message_count : 20},
	{topic : 'trump', message_count : 40},
	{topic : 'inventions', message_count: 120},
	{topic : 'skills', message_count : 160},
	{topic : 'trump', message_count : 50},
	{topic : 'inventions', message_count: 100},
	{topic : 'skills', message_count : 10},
	{topic : 'trump', message_count : 50},
	{topic : 'inventions', message_count: 1},
	{topic : 'skills', message_count : 10},
	{topic : 'trump', message_count : 50},
	{topic : 'inventions', message_count: 100},
	{topic : 'skills', message_count : 10},
	{topic : 'trump', message_count : 50},
	{topic : 'inventions', message_count: 100},
	{topic : 'skills', message_count : 10},
	{topic : 'trump', message_count : 50}
];

//note: GLOBAL!! Required elsewhere
searched = []; //this will record any combination of search phrases and topics

function ready() {
	//set up d3 visualization pane
	d3.select("#input-topic").on("keydown", function() {
	  var e = d3.event;
	  if (e.which === 13 || e.which === 10) {
	    e.preventDefault();
		var searchPhrase = d3.select(this).text();
		searched = [searchPhrase];
	    return newTopic(searchPhrase);
	  }
	}).on("click", function() {
	  return d3.select(this).text("");
	});
	
	//set up message panel
	setupMessagePanel();
}

function newTopic(topic) {
	var searchPhrase = topic;
	callBackend("top_topics_by_search_phrase", {search_phrase: topic, limit: 20}, function(err, rspns) {
		if (!err) {	//if no error in request
			var relatedTopics = rspns.top_topics;

			console.log(relatedTopics);
			//pull out itself if its in the response
			var searchTopic = null;
			var searchTopicIndex;
			for (var i=0; i<relatedTopics.length; i++) {
			  var t = relatedTopics[i];
			  if (t.topic === topic) {
				searchTopic = t;
				searchTopicIndex = i;
				break;
			  }
			}
			if (searchTopic != null) {	//is part of the topic set
				searchTopic['isSearchTerm'] = true;
				relatedTopics.splice(searchTopicIndex, 1); // Remove entry in relatedTopics
				var visualization = visualizer(d3.select("#topics"), searchTopic, relatedTopics, function (topic) {console.log(topic);});
			} else {
				console.log("response related topics does not contain the searched phrase");
				console.log("reverting to separate parameter search_phrase_matches with value" + rspns.search_phrase_matches);
				var visualization = visualizer(d3.select("#topics"), {topic: searchPhrase, message_count : rspns.search_phrase_matches, isSearchTerm: true}, relatedTopics, function (topic) {console.log(topic);});
			}
			visualization.run();

			print_messages(topic);
		} else {
			console.log("error ocurred, using default");
			var visualization = visualizer(d3.select("#topics"), testSearchTopic, testRelatedTopics, function (topic) {console.log(topic);});
			visualization.run();	
		}
	});
		
}
