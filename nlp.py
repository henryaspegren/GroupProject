import os, re
from nltk.tag.stanford import StanfordNERTagger
from sql_client import MySQLSession, ForumMessage, MessageTopic, Topic, MessageQuote, Quote, User
from nltk.tokenize import TweetTokenizer

NLP_ROOT = os.getcwd()+'/stanford-ner/'
# alternative: english.all.3class.distsim.crf.ser.gz
NER_CLASSIFIER = 'english.conll.4class.distsim.crf.ser.gz'

database_connection = MySQLSession().get_session()

"""
Class that abstracts away topic extraction
"""
class TopicExtractor(object):

	def __init__(self, tokenizer_model=TweetTokenizer(), ner_model=NER_CLASSIFIER, 
		nlp_root=NLP_ROOT):
		self.tokenizer = tokenizer_model
		self.ner_tagger = StanfordNERTagger(nlp_root+'classifiers/'+ner_model, 
			path_to_jar=(NLP_ROOT+'stanford-ner.jar'))

	def extract_topics(self, message):
		message_text = message.get_post()
		tokens = self.tokenizer.tokenize(message_text)
		res = self.ner_tagger.tag(tokens)
		named_entities = set()
		for (token, tag) in res:
			# O corresponds to no named entity
			if tag != 'O':
				named_entities.add(token)
		return named_entities

	def extract_user_mentions(self, message):
		message_text = message.get_post()
		tokens = self.tokenizer.tokenize(message_text)
		user_mentions = set()
		for token in tokens:
			if token[0] == '@':
				user_mentions.add(token)
		return user_mentions
"""
Class for message processing
"""
class Processing(object):

	def __init__(self, session=MySQLSession().get_session(), topic_extractor=TopicExtractor()):
		self.session = session
		self.topic_extractor

	"""
	Processes a forum message by extracting topics from the message and
	storing the message topic(s) in the message_topics table and storing the
	topic(s) in the topics table (as well as incrementing the message count)
	"""
	# note that there can be problems if the session we are using
	# is not consistent with the session connected to the message
	# object passed in.
	def extract_message_topic_to_db(self, message, db_session=None):
		# defaults to stored session
		if db_session is None:
			db_session = self.session
		topics = self.topic_extractor.extract_topics(message)
		message_id = message.get_message_id()
		for topic_str in topics:
			# search topic table for topic
			topic_row = db_session.query(Topic).filter(Topic.topic == topic_str).first()
			topic_id = None
			# new topic
			if topic_row is None:
				new_topic = Topic(topic=topic_str, message_count=1)
				print 'Adding new topic'
				db_session.add(new_topic)
				db_session.commit()
				print new_topic
				topic_id = new_topic.get_topic_id()
			# existing topic entry
			else:
				topic_id = topic_row.get_topic_id()
				topic_row.increment_message_count()
			# Now we have to put corresponding entry in the
			# message_topics table
			message_topic = db_session.query(MessageTopic).filter((MessageTopic.topic_id == topic_id) and (MessageTopic.message_id == message_id)).first()
			# if no entry put one in
			if message_topic is None:
				print 'Adding new message_topic'
				new_message_topic = MessageTopic(topic_id=topic_id, message_id=message_id)
				db_session.add(new_message_topic)
				db_session.commit()
				print new_message_topic
	"""
	Runs the message topic extraction on a database iterator
	"""
	def run_topic_extraction(self, message_iterator=None):
		if message_iterator is None:
			message_iterator = self.session.query(ForumMessage).order_by(ForumMessage.message_id)
		for msg in message_iterator:
			extract_message_topic_to_db(msg)

"""
Class for preprocessing and cleaning the message data
"""
class PreProcessing(object):

	# regex for quotes
	# NOTE that this always grabs the outermost quote. So nested quotes will
	# be treated text in the outermost quote
	quote_regex_expr = r'(\[quote id=(?P<quote_id>([0-9-])+)\](?P<text>[\W\w]+)\[/quote\])+'
	quote_regex = re.compile(quote_regex_expr, re.IGNORECASE)


	def __init__(self, session=MySQLSession().get_session()):
		self.session = session

	# note that there can be problems if the session we are using
	# is not consistent with the session connected to the message
	# object passed in.
	def remove_quotes_from_message_to_db(self, message, db_session=None):
		message_text = message.get_post()
		results = re.search(self.quote_regex, message_text)

		# default to use stored session
		if db_session is None:
			db_session = self.session

		print "original message is: \n '%s' \n" % message_text

		if results is not None:
			results_dictionary = results.groupdict()
			# extract fields
			quote_id = results_dictionary['quote_id']
			quote_text = results_dictionary['text']
			# clean the message by replacing the quote with the empty string
			cleaned_message_text = re.sub(self.quote_regex, '', message_text)
			# set the cleaned message text
			message.set_cleaned_post(cleaned_message_text)
			# first tie the message to the quote
			message_quote = db_session.query(MessageQuote).filter((MessageQuote.quote_id == quote_id) and (MessageQuote.message_id == message_id)).first()

			if message_quote is None:
				# add the message quote to the db
				message_quote = MessageQuote(quote_id=quote_id, message_id=message.get_message_id())
				db_session.add(message_quote)
			quote = db_session.query(Quote).filter(Quote.quote_id == quote_id).first()
			# then add the quote

			if quote is None:
				quote = Quote(quote_id=quote_id, quote_text=quote_text)
				db_session.add(quote)
			# else just update existing entry
			else:
				quote.set_quote_text(quote_text)

		else:
			# just use the original post
			message.set_cleaned_post(message.get_post())
		print "cleaned message is: \n '%s' \n" % message.get_cleaned_post()
		db_session.commit()


	def extract_user_mentions_to_db(self, session, message):
		topic_extractor = TopicExtractor()
		user_mentions = topic_extractor.extract_user_mentions()
		message_id = message.get_message_id()

		for mentioned_user in user_mentions:
			user_row = session.query(User).filter(User.user == mentioned_user)
			user_id = None

			if user_row is None:
				new_user = User(user = mentioned_user, user_count = 1)
				print 'Add new user'
				session.add(new_user)
				session.commit()
				print new_user
				user_id = new_user.get_user_id()
			else:
				user_id = user_row.get_user_id()
				user_row.increment_user_count()

		# remove the user mentions from the original message and store the clean message in the database

		#clean_message = session.query(ForumMessage).
		#session.query(ForumMessage).filter(ForumMessage.message_id = message_id).set_clean_message(clean_message);

	def run_user_mentions_extraction(self, session, message_iterator):
		if message_iterator is None:
			message_iterator = self.session.query(ForumMessage).order_by(ForumMessage.message_id)
		for msg in message_iterator:
			extract_user_mentions_to_db(msg)

#class Main(object):
#	processing = PreProcessing()
#	processing.run_user_mentions_extraction(session=MySQLSession(host='abc', port=3307).get_session(), message_iterator=None)











