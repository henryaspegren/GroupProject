import os, re, nltk, time
from nltk.tag.stanford import StanfordNERTagger
from nltk import word_tokenize
from sql_client import MySQLSession, ForumMessage, MessageTopic, Topic, MessageQuote, Quote, User
from nltk.tokenize import TweetTokenizer


NLP_ROOT = os.getcwd()+'/stanford-ner/'
# alternative: english.all.3class.distsim.crf.ser.gz
NER_CLASSIFIER = 'english.conll.4class.distsim.crf.ser.gz'

DEBUG = False

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
		self.topic_extractor = topic_extractor

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
				if DEBUG: 
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
				if DEBUG:
					print 'Adding new message_topic'
				new_message_topic = MessageTopic(topic_id=topic_id, message_id=message_id)
				db_session.add(new_message_topic)
				db_session.commit()
				if DEBUG:
					print new_message_topic
	"""
	Runs the message topic extraction on a database iterator
	"""
	def run_topic_extraction(self, message_iterator=None):
		if message_iterator is None:
			message_iterator = self.session.query(ForumMessage).order_by(ForumMessage.message_id)
		
		start_time = time.time()
		total = message_iterator.count()
		number_processed = 0

		for msg in message_iterator:
			self.extract_message_topic_to_db(msg)

			number_processed += 1
			# simple log to see how much progress we has been made
			if (number_processed % 1000 == 0):
				elapsed_time = (time.time()-start_time)
				print "Processed : %i of %i in %s" % (number_processed, total, str(elapsed_time))

"""
Class for preprocessing and cleaning the message data
"""
class PreProcessing(object):

	# regex for quotes
	# NOTE that this always grabs the outermost quote. So nested quotes will
	# be treated text in the outermost quote
	quote_regex_expr = r'(\[quote id=(?P<quote_id>([0-9-])+)\](?P<text>[\W\w]+)\[/quote\])+'
	quote_regex = re.compile(quote_regex_expr, re.IGNORECASE)
	users_regex_expr = r'@([a-\z][A-\Z][0-9])+'
	users_regex = re.compile(users_regex_expr)

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

		if DEBUG:
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

		if DEBUG:
			print "cleaned message is: \n '%s' \n" % message.get_cleaned_post()
		
		db_session.commit()

	# run quote extraction over a set of messages
	# if none is specified, then quote extraction will be run on the entire database
	def run_quotes_extraction(self, message_iterator=None):
		if message_iterator is None:
			message_iterator = self.session.query(ForumMessage).order_by(ForumMessage.message_id)
		
		start_time = time.time()
		total = message_iterator.count()
		number_processed = 0

		for msg in message_iterator:
			self.remove_quotes_from_message_to_db(msg)

			number_processed += 1
			# simple log to see how much progress we has been made
			if (number_processed % 1000 == 0):
				elapsed_time = (time.time()-start_time)
				print "Processed : %i of %i in %s" % (number_processed, total, str(elapsed_time))


	def extract_user_mentions_to_db(self, message):

		topic_extractor = TopicExtractor()
		message_text = message.get_post()
		tokens = topic_extractor.tokenizer.tokenize(message_text)
		user_mentions = topic_extractor.extract_user_mentions(message)
		message_id = message.get_message_id()

		for mentioned_user in user_mentions:
			user_row = self.session.query(User).filter(User.user == mentioned_user).first()
			user_id = None

			if user_row is None:
				new_user = User(user = mentioned_user, user_count = 1)
				if DEBUG:
					print 'Add new user'
				self.session.add(new_user)
				self.session.commit()
				if DEBUG:
					print new_user
				user_id = new_user.get_user_id()
			else:
				user_id = user_row.get_user_id()
				user_row.increment_user_count()

		# remove the user mentions from the original message and store the clean message in the database
		cleaned_message_text = re.sub(self.quote_regex, '', message_text)

		# set the cleaned message text
		message.set_cleaned_post(cleaned_message_text)

		#clean_message = session.query(ForumMessage).
		#session.query(ForumMessage).filter(ForumMessage.message_id = message_id).set_clean_message(clean_message);

	def run_user_mentions_extraction(self, message_iterator):
		if message_iterator is None:
			message_iterator = self.session.query(ForumMessage).order_by(ForumMessage.message_id)
		for msg in message_iterator:
			self.extract_user_mentions_to_db(msg)


class Main(object):


	def run(self, quote_extraction=False, mention_extraction=False, topic_extraction=False):

		print """Performing preprocessing and nlp with 
		quote_extraction   : %s
		mention_extraction : %s 
		topic_extraction   : %s\n""" % (str(quote_extraction), str(mention_extraction), str(topic_extraction)) 

		database_connection = MySQLSession(username='cstkilo', password='Kilo_Jagex', host='localhost', port=3307,
		database='cstkilo')

		pre_processing = PreProcessing(session=database_connection.get_session())
		processing = Processing(session=database_connection.get_session())

		if quote_extraction:
			print "___________________________________________________\n"
			print "           Starting Quote Extraction               \n"
			print "___________________________________________________\n"
			pre_processing.run_quotes_extraction()
			print "___________________________________________________\n"
			print "           Starting Quote Extraction               \n"
			print "___________________________________________________\n"
		if mention_extraction:
			print "___________________________________________________\n"
			print "        Starting User Mention Extraction           \n"
			print "___________________________________________________\n"
			pre_processing.run_user_mentions_extraction()
			print "___________________________________________________\n"
			print "        Finished User Mention Extraction           \n"
			print "___________________________________________________\n"

		if topic_extraction:
			print "___________________________________________________\n"
			print "           Starting Topic Extraction               \n"
			print "___________________________________________________\n"
			processing.run_topic_extraction()
			print "___________________________________________________\n"
			print "           Finished Topic Extraction               \n"
			print "___________________________________________________\n"





# run the main program
if __name__ == '__main__':
    Main().run(quote_extraction=True)






