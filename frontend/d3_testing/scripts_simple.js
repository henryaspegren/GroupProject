/*

	heavily based on
	http://bl.ocks.org/mbostock/4062045
	
	really going for something like, perhaps?
	
	http://www.redotheweb.com/CodeFlower/

*/



function visualizer(searchTopic, relatedTopics, widthFraction, heightFraction, onTopicClickCallback) {

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
	var searchTopics = searchTopic;
	//see next block of comments
	
	
	//-----------sample data---------------

	//past search queries, newest at the end
	//format matches JSON 'topics'
	//searchTopics[searchTopics.length-1] is newest, most specific, query term
	//var searchTopics = [{topic : 'test', number:500, isSearchTerm:true},{topic : 'jagex', number: 300, isSearchTerm : true}, {topic : 'rs', number: 200, isSearchTerm : true}];
	//above line: DEPRACATED as of REPACKAGE

	
	/*
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

	var topics = json_related_topics.topics;
	var combinedTopics = [searchTopics[searchTopics.length-1]].concat(topics);
	var numSearchedTopics = searchTopics.length;

	var links = computeLinks(combinedTopics);
	var force = d3.layout.force()
		//.charge(-30)
		//.linkDistance(200)
		.charge(function(d) { return calcRadius(d)/MIN_RADIUS * topics.length*-75; }) //repulsion force depends on radius of circle and number of topics in this circle
		.linkDistance(function(d) { return MIN_DIST + 50*(5 - 5*Math.pow(1.15,-json_number_matching_search.number/(d.target.number)));} )
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
			return Math.max(MIN_RADIUS,MAX_RADIUS * (node.number/json_number_matching_search.number));
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

		var svg = d3.select("body").append("svg")
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
				.attr("class", "link"); //could do a per-link styling for link thickness here

		var node = svg.selectAll(".node")
			.data(combinedTopics)
			.enter().append("g")
			.attr("class", "node")
			//for callback that a node has been clicked on!
			.on("click", function (d) {
				animateSelectedNode(this);
				console.log("Selected: " + d);
				//callback(d);
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

}


