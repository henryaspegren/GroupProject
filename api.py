from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions
from sql_client import MySQLSession, ForumMessage, MessageTopic, Topic
import operator, collections

app = FlaskAPI(__name__)


DEFAULT_LIMIT = 10

# To Ping API:
# curl -H "Content-Type: application/json" -X POST -d '{"limit": 10, "topic": 
# "Demons"}' http://127.0.0.1:5000/search_topic/

database_connection = MySQLSession().get_session()

"""
API for looking up messages that contain a search phrase

Request: {'phrase' : <string to search form>
			'limit' : <max number of messages to return> }
Response: {'length' : <number of messages> 
			'messages' : [<list of messages in json format>]}

"""
@app.route("/search_phrase/", methods=['POST'])
def search_phrase():
	if request.method != 'POST':
		# todo: error message
		pass
	else: 
	    phrase = str(request.data.get('phrase'))
	    limit = int(request.data.get('limit'))
	    if limit is None:
	    	limit = DEFAULT_LIMIT
	    print "searching for messages containing: '%s' with limit: '%i'" % (phrase, limit)
	    messages = database_connection.query(ForumMessage).filter(ForumMessage.post.like('%'+phrase+'%')).limit(limit)
	    number_of_messages = 0
	    results = []
	    for message in messages:
	    	results.append(message.to_json())
	    	number_of_messages += 1
	    return {'length': number_of_messages, 'messages': results }, status.HTTP_200_OK


"""
API for returning messages that contain a given topic (topic id)

Request: {'topic_id' : <topic_id>
			'limit' : <max number of messages to return>}
Response: {'length' : <number of messages> 
			'messages' : [<list of messages in json format>]}

"""
@app.route("/search_topic/", methods=['POST'])
def search_topic():
	if request.method != 'POST':
		# todo: error message
		pass
	else:
		topic_id = str(request.data.get('topic_id'))
		limit = int(request.data.get('limit'))
		if limit is None:
			limit = DEFAULT_LIMIT
		print "searching messages with topic_id: '%s' with limit: '%s'" % (topic, limit)		
		# look up the message ids with that topic
		message_ids = database_connection.query(MessageTopic).filter(MessageTopic.topic_id == topic_id).limit(limit)
		if message_ids is None:
			api_data = { 'length': 0, 'messages' : [] }
		else:
			# now get the messages themseleves
			messages = []
			for message_id in [x.get_message_id() for x in message_ids]:
				# lookup the message
				message = database_connection.query(ForumMessage).filter(
					ForumMessage.message_id == message_id).one()
				messages.append(message.to_json())
			# return using the response format
			api_data = {'length': len(messages), 'messages' : messages}
		return api_data, status.HTTP_200_OK

"""
API for returning top topics in messages containing a search phrase

TODO: pretty sure this isn't going to be scalable

Request: {'search_phrase' : <message_topic> 
			'limit' : <max number of messages to return> }
Response: {'length' : <number of messages> 
			'top_topics : [
				{	topic : <topic_name>,
					topic_id : <topic_id>
					message_count : <number_of_messages_in_this_topic>
				},
				{	topic : <topic2_name>,
					topic_id : <topic_id2>
					message_count : <number_of_messages_in_this_topic>
				}
				]
		    }
"""
@app.route("/top_topics_by_search_phrase/", methods=['POST'])
def top_topics_by_search_phrase():
	if request.method != 'POST':
		# todo: error message
		pass
	else:
		search_phrase = str(request.data.get('search_phrase'))
		limit = int(request.data.get('limit'))
		if limit is None:
			limit = DEFAULT_LIMIT
		print "top topics among messages containing: '%s' with limit: '%s'" % (search_phrase, limit)	

		topics = database_connection.query(Topic).join(MessageTopic).join(ForumMessage).filter(ForumMessage.post.like('%'+search_phrase+'%')).order_by(Topic.message_count.desc()).limit(limit)

		if topics is None:
			api_data = {'length': 0, 'top_topics' : []}
		else:
			top_topics = []
			for topic in topics:
				top_topics.append(topic.to_json())
			api_data = {'length': len(top_topics), 'top_topics' : top_topics}
		return api_data, status.HTTP_200_OK


"""
API for returning the top topics by number of messages. Later we can 
group these hierarchically 

Request: {"limit" : <max number of topics to return> }
Response: {"name" : "Top Topics", 
			"children" : [
				{ "name" : <topic>,  "size" : <num messages> },
				{ "name" : <topic2>, "size" : <num messages> }
			]
		}
"""
@app.route("/top_topics/", methods=['POST'])
def top_topics():
	if request.method != 'POST':
		pass
	else:
		limit = int(request.data.get('limit'))
		if limit is None:
			limit = DEFAULT_LIMIT
		topics = database_connection.query(Topic).order_by(Topic.message_count.desc()).limit(limit)
		top_topics = [{"name" : topic.get_topic(), "size" : topic.get_message_count()} for topic in topics]
		api_data = {"name": "Top Topics", "children" : top_topics}
		return api_data, status.HTTP_200_OK


if __name__ == "__main__":
    app.run(debug=True)