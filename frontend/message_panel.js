function setupMessagePanel() {
	$("#right").scroll(function () {
		// Infinite scroll -- when reach bottom, request more messages and append them to "left"
		var height = $(this).scrollHeight - $(this).height(); // Get the height of the div
		var scroll = $(this).scrollTop(); // Get the vertical scroll position
		var isScrolledToEnd = (scroll >= height);
		$(".scroll-pos").text(scroll);
		$(".scroll-height").text(height);
		if (isScrolledToEnd) {
			console.log("hit end of messages, getting more");
			//extend current list of message
			var json = { phrase: theme, limit: 50 };
			post("search_phrase", json, searchPhraseCallback);
		}
	});	
}

//appends to current list of messages the new ones we received
function searchPhraseCallback(err,data){
	for (var i=0; i<data.messages.length;i++) {		
		
		var text = data.messages[i].post;
		var regex = new RegExp("(\\b" + searched[searched.length - 1].trim() + "\\b)", "gim");
		var res = text.replace(regex, '<span class = "highlight"> $1 </span>');
		var line = data.messages[i].user_id + ": " + res;
		
		var textContainer = document.createElement('div');
		$(textContainer).addClass("messageContainer")
			.html(line)
			.appendTo($("#right"));
	}
};

//clear message panel
function clearMessagePanel() {
	$("#right").empty();	//remove all children
}

//this gets called when the searched phrase has changed
function updateMessagesPanel(phrase) {
	var json = { phrase: phrase, limit : 50};
	clearMessagePanel();
	post("search_phrase", json, searchPhraseCallback);
}
