var theme;

$(document).ready(function () {
	$("#right").scroll(function () {
		// Infinite scroll -- when reach bottom, request more messages and append them to "left"
		var $this = $(this);
		var height = this.scrollHeight - $this.height(); // Get the height of the div
		var scroll = $this.scrollTop(); // Get the vertical scroll positio
		var isScrolledToEnd = (scroll >= height);
		$(".scroll-pos").text(scroll);
		$(".scroll-height").text(height);
		if (isScrolledToEnd) {
			var json = { phrase: theme, limit: 50 };
			callBackend("search_phrase", json, searchPhraseCallback);
		}
	});
});

function searchPhraseCallback(err,data){
	for (var i=0; i<data.messages.length;i++) {
		var text = data.messages[i].post;
		var query = new RegExp("(\\b" + theme + "\\b)", "gim");
		var res = text.replace(query, '<span class = "highlight"> $1 </span>');
		var currentLine = data.messages[i].user_id + ": " + res;
		$("#right").append(currentLine+"<br> </br>");
	}
};

function print_messages(topic) {
	theme = topic;
	var json = { phrase: topic, limit: 50 };
	callBackend("search_phrase", json, searchPhraseCallback);
};