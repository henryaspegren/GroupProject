function loaded() {

var data = [4, 8, 15, 16, 23, 42];

d3.select("#chart")
  .selectAll("div")
    .data(data)
  .enter().append("div")
    .style("width", function(d) { return d * 10 + "px"; })
    .text(function(d) { return d; });
	
}


//define a topic object
//options for  
topic = function(name, number, options) {


}