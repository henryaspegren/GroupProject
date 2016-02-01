from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions
from sql_client import MySQLSession, ForumMessage, MessageTopic, Topic

app = FlaskAPI(__name__)


DEFAULT_LIMIT = 10

# To Ping API:
# curl -H "Content-Type: applicati-d '{"limit": 10,"search_phrase":"Jagex"}' http://127.0.0.1:5000/search_phrase/


database_connection = MySQLSession().get_session()


"""
Simple API for looking up messages that contain a search phrase.
TODO: adapt this to work with topics (shouldn't be hard)
"""
@app.route("/search_phrase/", methods=['POST'])
def search_phrase():
	if request.method != 'POST':
		# todo: error message
		pass
	else: 
	    phrase = str(request.data.get('search_phrase'))
	    limit = int(request.data.get('limit'))
	    if limit is None:
	    	limit = DEFAULT_LIMIT
	    print "searching: '%s' with limit: '%i'" % (phrase, limit)
	    messages = database_connection.query(ForumMessage).filter(ForumMessage.post.like('%'+phrase+'%')).limit(limit)
	    number_of_messages = 0
	    results = []
	    for message in messages:
	    	results.append(message.to_json())
	    	number_of_messages += 1
	    return {'length': number_of_messages, 'messages': results }, status.HTTP_200_OK


"""
API for returning 

"""
@app.route("/search_topic/", methods=['POST'])
def search_topic():
	if request.method != 'POST':
		# todo: error message
		pass
	else:
		topic = str(request.data.get('topic'))
		limit = int(request.data.get('limit'))
		if limit is None:
			limit = DEFAULT_LIMIT
		messages = database_connection.query(ForumMessage).filter(ForumMessage.post.like('%'+phrase+'%')).limit(limit)
		for message in messages:
			message_id = message.get_message_id()			
	return {'test': 'hello'}, status.HTTP_200_OK


if __name__ == "__main__":
    app.run(debug=True)