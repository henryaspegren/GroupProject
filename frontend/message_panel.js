var offset = 0;

function setupMessagePanel() {
	offset = 0;
	$("#right").scroll(function () {
		// Infinite scroll -- when reach bottom, request more messages and append them to "left"
		/*  +------------------------+  --+---------+
     *  |                        |    |         |  scrollTop
		 *  |------------------------+  --|----+----V
		 *  |                        |    |    |  clientHeight
		 *  |------------------------+  --|----V
		 *  |                        |    | scrollHeight
		 *  +------------------------+  --V
		 */
		var remainingHeight = this.scrollHeight - ( this.scrollTop + this.clientHeight );
		var isScrolledToEnd = remainingHeight <= 30;
		if (isScrolledToEnd) {
			//extend current list of message
			var json = { phrase_list: searched, limit: 20, offset: offset };
			console.log("Hit end of messages. Requesting "+json.limit+" more, starting from "+json.offset);
			post("messages_with_phrase_list", json, searchPhraseCallback); // ((offset is updated in here))
		}
	});
}

//appends to current list of messages the new ones we received
function searchPhraseCallback(err,data){
	if (!data) {
		console.log(err);
		return;
	}

	var m = data.messages;
	offset += m.length;

	for (var i=0; i<m.length; i++) {
		var curr = m[i];

		var sentiment = curr.sentiment;
		var text = curr.post;
		var res = text;
		// now highlights all the terms that we have searched for!
		for (var j=0; j<searched.length; j++){
			var regex = new RegExp("(" + searched[j].trim() + ")", "gim");
			res = res.replace(regex, '<span class = "highlight">$1</span>');
		}
		var line = curr.user_id + ": " + res;

		var textContainer = document.createElement('div');
		//console.log(sentiment);

		if(sentiment > 0.2)
			$(textContainer).addClass("messageContainerPositive")
				.html(line)
				.appendTo($("#right"));
		else if(sentiment < -0.2)
			$(textContainer).addClass("messageContainerNegative")
			.html(line)
			.appendTo($("#right"));
		else
		{
			$(textContainer).addClass("messageContainer")
			.html(line)
			.appendTo($("#right"));
			//el = document.getElementsByClassName(".messageContainer");
			//el.style.borderLeftStyle = "solid";
			//el.style.borderLeftWidth = "10px";
			//el.style.borderLeftColor = "blue";
		}
	}
};

//clear message panel
function clearMessagePanel() {
	$("#right").empty();	//remove all children
}

//this gets called when the searched phrase has changed
function updateMessagesPanel(phraseList) {
	offset = 0;
	var json = { phrase_list: phraseList, limit : 20};
	clearMessagePanel();
	post("messages_with_phrase_list", json, searchPhraseCallback);
}
