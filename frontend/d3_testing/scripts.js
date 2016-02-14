/*

	heavily based on
	http://bl.ocks.org/mbostock/4062045

*/





/*
arguments:
  topics
    list of all topic nodes, INCLUDING prior queries (may need to be added in elsewhere)
  n
    first 'n' topics in 'topics' are the prior queries, oldest to newest
  ie. if previously narrowed search through 'rs' and 'skills' 
  topics and n could be: ['rs', 'skills', 'inventions', 'dungeons'...]
returns:
	list of links, with the previousTopics linearly connected
	and newTopics all connected to the last topic in previousTopics (ie newest query)
*/
function computeLinks(topics, n) {
	links = [];
	for (var i = 1; i < n; i++) {
		links.push({source : i-1, target: i});
	}
	for (var i = n; i < topics.length; i++) {
		//could compute something here about link strength/boldness
		//using the source and target numbers perhaps
		links.push({source : n-1, target: i}); //connect current query to each node
	}
	
	return links;
}


//-----------sample data---------------

//past search queries, newest at the end
//format matches JSON 'topics'
var searchTopics = [{topic : 'jagex', number: 1, isSearchTerm : true}, {topics : 'rs', number: 1, isSearchTerm : true}];

json_related_topics = {
	topics : [
		{topic : 'inventions', number: 100},
		{topic : 'skills', number : 10},
		{topic : 'trump', number : 50},
	]
};

json_number_matching_search = {
	number : 200
}


var width = 960,
    height = 500;
	
var topics = json_related_topics.topics;
var combinedTopics = searchTopics.concat(topics);
var numSearchedTopics = searchTopics.length;

var links = computeLinks(combinedTopics, numSearchedTopics);

var force = d3.layout.force()
    //.charge(-30)
    //.linkDistance(200)
	.charge(function(d) { return d._children ? -d.size / 100 : -40; })
	.linkDistance(function(d) { d.isSearchTerm ? 100 : 50})
    .size([width, height]);


/*calculates radius size for a given topic
can make this proportional to total number in this topic
so when we do a deep dive can still read text/not have tiny bubbles

args:
  n
    number of messages this topic is mentioned in (within this deep dive!)
returns:
  radius
*/
function calcRadius(n) {
	//return n/numSearchedTopics; 	//TODO if we want to
	return 50;
}

function color(topic) {
	return "#aaa";
}

function loaded() {

	var svg = d3.select("body").append("svg")
		.attr("width", width)
		.attr("height", height);
		
	

	force
		.nodes(combinedTopics)
		.links(links)
		.start();
		
	//set up links and build them as per data needs
	var link = svg.selectAll('link')
			.data(links)
			.enter().append("line")
			.attr("class", "link"); //could do a per-link styling for link thickness here
	
	var node = svg.selectAll(".node")
			.data(combinedTopics)
			.enter().append("circle")
			.attr("class", "node")
			.attr("r", function(d) { return calcRadius(d.number); })
			.style("fill", function(d) { return color(d); })
			.call(force.drag);
	
	//set text
	node.append("title").text(function(d) {return d.topic;});
	
	//to do with animations
	force.on("tick", function() {
		link.attr("x1", function(d) { return d.source.x; })
			.attr("y1", function(d) { return d.source.y; })
			.attr("x2", function(d) { return d.target.x; })
			.attr("y2", function(d) { return d.target.y; });

		node.attr("cx", function(d) { return d.x; })
			.attr("cy", function(d) { return d.y; });
	});
}




