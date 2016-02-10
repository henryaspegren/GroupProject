$(document).ready(function () {			
	$("div").scroll(function () {
		// Infinite scroll -- when reach bottom, request more messages and append them to "left"
		var $this = $(this);
		var height = this.scrollHeight - $this.height(); // Get the height of the div
		var scroll = $this.scrollTop(); // Get the vertical scroll positio
		var isScrolledToEnd = (scroll >= height);
		$(".scroll-pos").text(scroll);
		$(".scroll-height").text(height);
		if (isScrolledToEnd) {
			//var moreMessages = request(topic, 50, linkToAPI); // Get 50 more messages ---- Not active because not yet connected to API
			
			var moreMessages = {number:3 , messages: [   {ID: "m1", user_ID: "user1", post:"Hello"}, // won't need this later
													   {ID: "m2", user_ID: "user2", post:"Hello2"} , 
													   {ID: "m3", user_ID: "user3", post:"Hello3"}] };
			for(var i=0;i<moreMessages.messages.length;i++){							
				$("#left").append(moreMessages.messages[i].user_ID + ": " + moreMessages.messages[i].post + "<br></br>"); // Append user:message
			}
		}
	});
});


//var request = function(topic, limit,linkToAPI){}		//This is the JSON request 
//	$.ajax({
//		url: localhost...,
//		data: {"topic":topic, "limit":limit}, 
//		type: "GET",
//		success: function (data) { 
//			var obj = JSON.parse(data);
//			return obj;		
//		}					
//	});
//};
				
var print = function () {
		// var messagesArray = request(topic,50,linkToAPI )
		var messagesArray = {number:3 , messages: [   {ID: "m1", user_ID: "user1", post:"Hello"},  // won't need this either
													   {ID: "m2", user_ID: "user2", post:"Hello2"} , 
													   {ID: "m3", user_ID: "user3", post:"Hello3"}] };
		for(var i=0; i<messagesArray.messages.length;i++){
			var currentLine = messagesArray.messages[i].user_ID + ": " + messagesArray.messages[i].post;
			$("#left").append(currentLine+"<br> </br>");
		}
				
};
print();
