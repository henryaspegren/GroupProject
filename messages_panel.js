var linkToAPI = "http://127.0.0.1:5000/top_topics_by_search_phrase/";


$(document).ready(function () {
	$("#left").scroll(function () {
		// Infinite scroll -- when reach bottom, request more messages and append them to "left"
		var $this = $(this);
		var height = this.scrollHeight - $this.height(); // Get the height of the div
		var scroll = $this.scrollTop(); // Get the vertical scroll positio
		var isScrolledToEnd = (scroll >= height);
		$(".scroll-pos").text(scroll);
		$(".scroll-height").text(height);
		if (isScrolledToEnd) {
			var json = new Object();
			json.phrase = topic;
			json.limit = 50;
			request(linkToAPI,topic,callback);
		}
	});
});



var request = function (url, topic, callback) {
	$.post({
         url: url,
         type: "POST",
         data: {phrase:topic, limit:50},
         dataType: "json",
         contentType: "application/json",
         success: callback(data)
	})
};

var callback = function(data){
	var obj = JSON.parse(data);
	for(var i=0; i<obj.messages.length;i++){
		var currentLine = obj.messages[i].user_ID + ": " + obj.messages[i].post;
		$("#left").append(currentLine+"<br> </br>");
	}
	
};


print_messages = function (topic) {
	var json = new Object();
	json.phrase = topic;
	json.limit = 50;
	request(linkToAPI,topic,callback);
	//var messagesArray = {
	//	number: 3,
	//	messages: [
	//		{ID: "m1", user_ID: "DragonSlayer_z0rg_0456", post: "I can't say how much I love "+topic},  // won't need this either
	//		{ID: "m2", user_ID: "x0x0xx_pk_x0xx0x", post: "JAGEX "+topic+" IS SO OP PLZ REMOVE THX"} ,
	//		{ID: "m3", user_ID: "BranstonPickle82", post: topic+" boss guide: 1. Go to "+topic+"'s lair. 2. Kill "+topic+". 3. ????? 4. Profit!"},
	//	]
	//};
};