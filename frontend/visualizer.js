/*

	heavily based on
	http://bl.ocks.org/mbostock/4062045

	really going for something like, perhaps?

	http://www.redotheweb.com/CodeFlower/

*/

function visualizer(parent, searchTopic, relatedTopics, onclickCallback) {

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

	//now: passed in as argument, of format { topic : 'test', number : 500}
	//this becomes the center bubble
	//TODO: this is bad since it modifies searchTopic argument
	searchTopic.isSearchTerm = true;

	/*
	sample relatedTopics:

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
	*/
	var width = parent.node().clientWidth,
	  	height = parent.node().clientHeight;

	//EDITABLE CONSTANTS
	var MAX_RADIUS = 120;
	var MIN_RADIUS = 30;
	var MIN_DIST = MAX_RADIUS*2.0;
	var MAX_DIST = Math.min(width, height) / 2 - MIN_RADIUS;

	var totalMessages = 0;
	relatedTopics.forEach(function(t) {
		totalMessages += t.message_count;
	});
	console.log(totalMessages);

	var topics = relatedTopics;
  searchTopic.fixed = true; // Keep focal in centre
  searchTopic.x = width/2;
  searchTopic.y = height/2;

	//combine to pass to computeLinks and for d3's internal usage
	var combinedTopics = [searchTopic].concat(topics);	//combinedTopics[0] must be search topic
	var numSearchedTopics = searchTopic.message_count;

	var links = computeLinks(combinedTopics);
	var force = d3.layout.force()
		.charge(function(d) { if (d.isSearchTerm) return 0; else return -100; }) //repulsion force depends on number of topics in this circle
		.linkDistance(function(d) { return smoothClamp(MIN_DIST, MAX_DIST, -1, 5, 2, 100 * d.target.message_count / totalMessages); } )
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
			return MAX_RADIUS;
		} else {
			return smoothClamp(MIN_RADIUS, MAX_RADIUS, 1, 10, 5, 100 * node.message_count / totalMessages);
		}
	}

  // I'm sure d3 must do this... but cba trying to fit it in when I know exactly what I want
	// min is the minimum radius / distance
	// max is the maximum radius / distance
	// sgn is the correlation (1 - val increases with x, -1 - val decreases)
	// c is the "centre" of the graph, with steepest slope, along the x axis
	// k is the "stretch" of the function
	// x is the input variable
	// Use FooPlot to tweak e.g. 120 + 190*(1 + tanh((x-10)/5))
	function smoothClamp(min, max, sgn, c, k, x) {
		var a = (max - min) / 2;
		return min + a * (1 + Math.tanh(sgn*(x - c) / k));
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
			.style("fill", "rgb(0,100,255)")
      .style("stroke", "rgb(0,75,192)");
	}


	//ACTUALLY MAKES IT RUN
	function run() {
		parent.select("svg").selectAll("*").remove();
		var svg = parent.select("svg")
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
			.attr("class", "node-circle");
			//.style("fill", function(d) { return color(d); });

		var c = node.append("text")
		   .attr("text-anchor", "middle")
		   .attr("class", "node-text");

		//topic name in circle
		c.append("tspan")
			.text(function(d) { return d.topic})
			/*.attr("textLength", function(d) {
				console.log(d);
				//some sort of working dynamic text shrinking
				//will need to modify the *7 for different fonts/font sizes
				return Math.min(1.8*calcRadius(d), d.topic.length*7)  + "px";})
			.attr("lengthAdjust", "spacingAndGlyphs");*/

		//number in circle, one line down and left align
		c.append("tspan")
			.text(function(d) {return d.message_count})
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
