/*
	heavily based on
	http://bl.ocks.org/mbostock/4062045

	really going for something like, perhaps?

	http://www.redotheweb.com/CodeFlower/
*/



function visualizer(parent, searchTopic, relatedTopics, widthFraction, heightFraction, onclickCallback) {

	/*
	arguments:
	  topics
	   list of topics matching current query
	   topics[0] MUST be last search query
	returns:
	  list of links connecting topics[0] to each other node

	*/
	function computeLinks(topics) {
		links = [];
		for (var i = 1; i < topics.length; i++) {
			//could compute something here about link strength/boldness
			//using the source and target numbers perhaps
			links.push({source : 0, target: i}); //connect current query to each node
		}
		return links;
	}

	//now: passed in as argument, of similar format { topic : 'test', number : 500}
	//TODO: this is bad since it modifies searchTopic argument
	searchTopic['isSearchTerm'] = true;
	//see next block of comments


	//-----------sample data---------------

	//past search queries, newest at the end
	//format matches JSON 'topics'
	//searchTopics[searchTopics.length-1] is newest, most specific, query term
	//var searchTopics = [{topic : 'test', number:500, isSearchTerm:true},{topic : 'jagex', number: 300, isSearchTerm : true}, {topic : 'rs', number: 200, isSearchTerm : true}];
	//above line: DEPRACATED as of REPACKAGE


	/*

	DEPRACATED:
		now only passed the below 'topics' list as an argument

	json_related_topics = {
		topics : [
			{topic : 'inventions', number: 150},
			{topic : 'skills', number : 100},
			{topic : 'trump', number : 50},
			{topic : 'inventions', number: 10},
			{topic : 'skills', number : 30},
			{topic : 'trump', number : 80},
			{topic : 'inventions', number: 110},
			{topic : 'skills', number : 20},
			{topic : 'trump', number : 40},
			{topic : 'inventions', number: 120},
			{topic : 'skills', number : 160},
			{topic : 'trump', number : 50},
			{topic : 'inventions', number: 100},
			{topic : 'skills', number : 10},
			{topic : 'trump', number : 50},
			{topic : 'inventions', number: 1},
			{topic : 'skills', number : 10},
			{topic : 'trump', number : 50},
			{topic : 'inventions', number: 100},
			{topic : 'skills', number : 10},
			{topic : 'trump', number : 50},
			{topic : 'inventions', number: 100},
			{topic : 'skills', number : 10},
			{topic : 'trump', number : 50}
		]
	};

	*/


	//EDITABLE CONSTANTS
	var MAX_RADIUS = 120;
	var MIN_RADIUS = 30;
	var MIN_DIST = MAX_RADIUS;
	var X_SIZE = widthFraction; //percent in X and Y directions of screen to take up
	var Y_SIZE = heightFraction;

	var width = window.innerWidth*X_SIZE,
		height = window.innerHeight*Y_SIZE;

	var topics = relatedTopics;
	//combine to pass to computeLinks and for d3's internal usage
	var combinedTopics = [searchTopic].concat(topics);
	var numSearchedTopics = searchTopic.number;

	var links = computeLinks(combinedTopics);
	var force = d3.layout.force()
		.charge(function(d) { return calcRadius(d)/MIN_RADIUS * topics.length*-75; }) //repulsion force depends on radius of circle and number of topics in this circle
		.linkDistance(function(d) { return MIN_DIST + 50*(5 - 5*Math.pow(1.15,-searchTopic.number/(d.target.number)));} )
		.size([width, height]);




	/*calculates radius size for a given topic
	based on some kind of decay function I didn't really think about...
	want small insignificant circles further out
	args:
	  node
		node itself
	returns:
	  radius
	*/
	function calcRadius(node) {
		if (node.isSearchTerm) {
			return MAX_RADIUS*0.8;
		} else {
			return Math.max(MIN_RADIUS,MAX_RADIUS * (node.number/searchTopic.number));
		}
	}

	//edit this if different colors based on topic data wanted
	function color(node) {
		return "#aaa";
	}

	//edit this for changing on click animation
	function animateSelectedNode(nodeRef) {
		d3.select(nodeRef).select('circle')
		  .transition()
			.duration(500)
			.style("fill", "rgb(0,100,255)");
	}


	//ACTUALLY MAKES IT RUN
	function run() {

		console.log(parent[0]);

		var svg = parent.append("svg")
			.attr("width", width)
			.attr("height", height);

		svg.append("svg:rect")
			.style("stroke", "#999")
			.style("fill", "#fff")
			.attr('width', width)
			.attr('height', height);

		force
			.nodes(combinedTopics)
			.links(links)
			.start();

		//set up links and build them as per data needs
		var link = svg.selectAll('link')
				.data(links)
				.enter().append("line")
				.attr("class", "node-link"); //could do a per-link styling for link thickness here

		var node = svg.selectAll(".node")
			.data(combinedTopics)
			.enter().append("g")
			.attr("class", "node")
			//for callback that a node has been clicked on!
			.on("click", function (d) {
				animateSelectedNode(this);
				console.log("Selected: " + d);
				onclickCallback(d);
				});


		var n = node.append("circle")
			.attr("r", function(d) {return calcRadius(d); })
			.attr("class", "node-circle")
			.style("fill", function(d) { return color(d); });

		var c = node.append("text")
		   .attr("text-anchor", "middle")
		   .attr("class", "node-text");

		//topic name in circle
		c.append("tspan")
			.text(function(d) { return d.topic})
			.attr("textLength", function(d) {
				console.log(d);
				//some sort of working dynamic text shrinking
				//will need to modify the *7 for different fonts/font sizes
				return Math.min(1.8*calcRadius(d), d.topic.length*7)  + "px";})
			.attr("lengthAdjust", "spacingAndGlyphs");

		//number in circle, one line down and left align
		c.append("tspan")
			.text(function(d) {return d.number})
			.attr("dy", "1em")
			.attr("x", "0");


		//to do with animations
		force.on("tick", function() {
			link.attr("x1", function(d) { return d.source.x; })
				.attr("y1", function(d) { return d.source.y; })
				.attr("x2", function(d) { return d.target.x; })
				.attr("y2", function(d) { return d.target.y; });

			node.attr("cx", function(d) { return d.x; })
				.attr("cy", function(d) { return d.y; });

			node.attr("transform", function(d) {return "translate(" + d.x + "," + d.y + ")"; })
		});
	}

	return {
		run : run
	}
}


/* test data */

//WOULD BE GREAT IF IT WERE LOGICAL
//AND searchTopic.number > relatedTopics.__.number
//ie. none of the subtopics are in more messages than the searchTopic
//ASSUME: relatedTopics are all within searchTopic
var searchTopic = {topic : 'runescape', number : 200};

var relatedTopics = [
	{topic : 'inventions', number: 150},
	{topic : 'skills', number : 100},
	{topic : 'trump', number : 50},
	{topic : 'inventions', number: 10},
	{topic : 'skills', number : 30},
	{topic : 'trump', number : 80},
	{topic : 'inventions', number: 110},
	{topic : 'skills', number : 20},
	{topic : 'trump', number : 40},
	{topic : 'inventions', number: 120},
	{topic : 'skills', number : 160},
	{topic : 'trump', number : 50},
	{topic : 'inventions', number: 100},
	{topic : 'skills', number : 10},
	{topic : 'trump', number : 50},
	{topic : 'inventions', number: 1},
	{topic : 'skills', number : 10},
	{topic : 'trump', number : 50},
	{topic : 'inventions', number: 100},
	{topic : 'skills', number : 10},
	{topic : 'trump', number : 50},
	{topic : 'inventions', number: 100},
	{topic : 'skills', number : 10},
	{topic : 'trump', number : 50}
];

function ready() {
	var visualization = visualizer(d3.select('body'), searchTopic, relatedTopics,
								0.7, 1.0, function (topic) {console.log(topic);});
	visualization.run();
}
