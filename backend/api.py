from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions
from sql_client import MySQLSession, ForumMessage, MessageTopic, Topic
from sqlalchemy import func, desc, and_
import operator, collections

app = FlaskAPI(__name__)

DEFAULT_LIMIT = 10
DEFAULT_OFFSET = 0

# To Ping API:
# curl -H "Content-Type: application/json" -X POST -d '{"limit": 10, "topic_id":
# "Demons"}' http://127.0.0.1:5000/search_topic/

database_connection = MySQLSession().get_session()

"""
API for looking up messages that contain a search phrase. They are returned in the order of increasing message ID. The limit restricts the number of messages returned (defaults to a limit of 10). The offset specifies the number of messages to skip (defaults to 0) to make it possible for multiple API calls to go through all the results.
"""
@app.route("/messages_with_phrase/", methods=['POST'])
def messages_with_phrase():
	if request.method != 'POST':
		# todo: error message
		pass
	else: 
	    phrase = request.data.get('phrase')
	    limit = request.data.get('limit')
	    offset = request.data.get('offset')
	    if limit is None:
	    	limit = DEFAULT_LIMIT
	    if offset is None:
	    	offset = DEFAULT_OFFSET
	    print "searching for messages containing: '%s' with limit: '%i' and offset : '%i'" % (phrase, limit, offset)
	    messages = database_connection.query(ForumMessage) \
	    	.filter(ForumMessage.cleaned_post.like('%'+phrase+'%')) \
	    	.order_by(ForumMessage.message_id) \
	    	.offset(offset) \
	    	.limit(limit) 
	    number_of_messages = 0
	    results = []
	    for message in messages:
	    	results.append(message.to_json())
	    	number_of_messages += 1
	    return {'length': number_of_messages, 'messages': results }, status.HTTP_200_OK


@app.route("/messages_with_phrase_list/", methods=['POST'])
def messages_with_phrase_list():
	if request.method != 'POST':
		# todo: error message
		pass
	else: 
	    phrase_list = request.data.get('phrase_list')
	    limit = request.data.get('limit')
	    offset = request.data.get('offset')
	    if limit is None:
	    	limit = DEFAULT_LIMIT
	    if offset is None:
	    	offset = DEFAULT_OFFSET
	    messages = database_connection.query(ForumMessage)
	    #for phrase in phrase_list:
			#messages = messages.filter(ForumMessage.post.like('%'+phrase+'%'))
	    messages = messages.filter(and_(*[ForumMessage.cleaned_post.like('%'+phrase+'%') for phrase in phrase_list]))

	    messages = messages.order_by(ForumMessage.message_id) \
	    	.offset(offset) \
	    	.limit(limit) 
	    number_of_messages = 0
	    results = []
	    for message in messages:
	    	results.append(message.to_json())
	    	number_of_messages += 1
	    return {'length': number_of_messages, 'messages': results }, status.HTTP_200_OK



"""
API for returning messages that contain a given topic (topic id). They are returned in order of increasing message ID. The limit restricts the number of messages returned (defaults to a limit of 10). The offset specifes the number of messages to skip (defaults to 0) to make it possible for multiple API calls to go through all the results .
"""
@app.route("/search_topic/", methods=['POST'])
def search_topic():
	if request.method != 'POST':
		# todo: error message
		pass
	else:
		topic_id = request.data.get('topic_id')
		limit = request.data.get('limit')
		offset = request.data.get('offset')
		if limit is None:
			limit = DEFAULT_LIMIT
		if offset is None:
			offset = DEFAULT_OFFSET
		print "searching messages with topic_id: '%s' with limit: '%s' offset: '%s'" % (topic_id, limit, offset)		
		# look up the message ids with that topic
		message_ids = database_connection.query(MessageTopic) \
			.filter(MessageTopic.topic_id == topic_id) \
			.order_by(MessageTopic.message_id) \
			.offset(offset) \
			.limit(limit)
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
API for returning top topics in messages containing a search phrase. They are returned in order of the number of messages per topic (containing the search phrase). The limit specifies the maximum number of topics that can be returned. The offset allows specifies the number of topics to skip. 
"""
@app.route("/top_topics_by_search_phrase/", methods=['POST'])
def top_topics_by_search_phrase():
	if request.method != 'POST':
		# todo: error message
		pass
	else:
		search_phrase = request.data.get('search_phrase')
		if search_phrase is None:
			search_phrase = ""
		limit = request.data.get('limit')
		offset = request.data.get('offset')
		if limit is None:
			limit = DEFAULT_LIMIT
		if offset is None:
			offset = DEFAULT_OFFSET
		print "top topics among messages containing: '%s' with limit: '%s' offset: '%s'" % (search_phrase, limit, offset)	

		number_of_messages_containing_phrase = database_connection.query(ForumMessage).filter(ForumMessage.post.like('%'+search_phrase+'%')).count()

		res = database_connection.query(ForumMessage, MessageTopic, Topic,
				func.count(MessageTopic.topic_id).label('qty'), func.avg(ForumMessage.sentiment).label('sentiment')) \
			.join(MessageTopic) \
			.join(Topic) \
			.filter(ForumMessage.cleaned_post.like('%'+search_phrase+'%')) \
			.group_by(MessageTopic.topic_id) \
			.order_by(desc('qty')) \
			.offset(offset) \
			.limit(limit)

		if res is None:
			api_data = {'length': 0, 'top_topics' : []}
		else:
			top_topics = []
			for (forum_message, message_topic, topic, qty, sentiment) in res:
				top_topics.append({'topic': topic.topic, 
					'topic_id': topic.topic_id, 'message_count' : qty, 'sentiment': sentiment})
			api_data = {'length': len(top_topics), 'top_topics' : top_topics, 'search_phrase_matches' : number_of_messages_containing_phrase}
		return api_data, status.HTTP_200_OK

"""
API for returning top topics in messages containing a list of search phrases. They are returned in order of the number of messages per topic (containing the search phrases). The limit specifies the maximum number of topics that can be returned. The offset allows specifies the number of topics to skip. 
"""	
@app.route("/top_topics_by_search_phrase_list/", methods=['POST'])
def top_topics_by_search_phrase_list():
	if request.method != 'POST':
		# todo: error message
		pass
	else:
		search_phrase_list = request.data.get('phrase_list')
		if search_phrase_list is None:
			search_phrase_list = ""
		limit = request.data.get('limit')
		offset = request.data.get('offset')
		if limit is None:
			limit = DEFAULT_LIMIT
		if offset is None:
			offset = DEFAULT_OFFSET
		print "top topics among messages containing: [%s] with limit: '%s' offset: '%s'" % (",".join(search_phrase_list), limit, offset)	

		number_of_messages_containing_phrase = \
			database_connection.query(ForumMessage) \
				.filter(and_(*[ForumMessage.post.like('%'+search_phrase+'%') for search_phrase in search_phrase_list])) \
				.count()

		res = database_connection.query(ForumMessage, MessageTopic, Topic,
				func.count(MessageTopic.topic_id).label('qty'), func.avg(ForumMessage.sentiment).label('sentiment')) \
			.join(MessageTopic) \
			.join(Topic) \
			.filter(and_(*[ForumMessage.cleaned_post.like('%'+search_phrase+'%') for search_phrase in search_phrase_list])) \
			.group_by(MessageTopic.topic_id) \
			.order_by(desc('qty')) \
			.offset(offset) \
			.limit(limit)

		if res is None:
			api_data = {'length': 0, 'top_topics' : []}
		else:
			top_topics = []
			for (forum_message, message_topic, topic, qty, sentiment) in res:
				top_topics.append({'topic': topic.topic, 
					'topic_id': topic.topic_id, 'message_count' : qty, 'sentiment': sentiment})
			api_data = {'length': len(top_topics), 'top_topics' : top_topics, 'search_phrase_matches' : number_of_messages_containing_phrase}
		return api_data, status.HTTP_200_OK

"""
API for returning the top topics by number of messages. Later we can 
group these hierarchically 
"""
@app.route("/top_topics/", methods=['POST'])
def top_topics():
	if request.method != 'POST':
		pass
	else:
		limit = request.data.get('limit')
		if limit is None:
			limit = DEFAULT_LIMIT
		topics = database_connection.query(Topic).order_by(Topic.message_count.desc()).limit(limit)
		top_topics = [{"name" : topic.get_topic(), "size" : topic.get_message_count()} for topic in topics]
		api_data = {"name": "Top Topics", "children" : top_topics}
		return api_data, status.HTTP_200_OK



"""
API for returning the top topics by number of messages in each forum. They are returned in the order of the number of messages. 
"""
@app.route("/top_topics_by_forum/", methods=['POST'])
def top_topics_by_forum():
	if request.method != 'POST':
		pass
	else:
		limit = request.data.get('limit')
		if limit is None:
			# default limit here is 5
			limit = 5
		forums = database_connection.query(ForumMessage.forum_name).distinct()
		top_topics_keyed_by_forum = []
		for forum_res in forums:
			# forum name is the first element of the results tuple
			forum_name = forum_res[0]
			top_results = database_connection.query(ForumMessage, MessageTopic, Topic, func.count(MessageTopic.topic_id).label('qty')) \
				.join(MessageTopic) \
				.join(Topic) \
				.filter(ForumMessage.forum_name == forum_name) \
				.group_by(MessageTopic.topic_id) \
				.order_by(desc('qty')) \
				.limit(limit)
			top_topics_in_forum = []
			for (forum_message, message_topic, topic, quantity) in top_results:
				top_topics_in_forum.append(topic.get_topic())
			top_topics_keyed_by_forum.append([forum_name, top_topics_in_forum])
		return {"data" : top_topics_keyed_by_forum}, status.HTTP_200_OK


if __name__ == "__main__":
   app.run(debug=True)