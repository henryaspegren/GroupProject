import os, re, time, sys, ner
import os, re, nltk, time, sys, ner, textblob
from nltk.tag.stanford import StanfordNERTagger
from nltk import word_tokenize
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from sql_client import MySQLSession, ForumMessage, MessageTopic, Topic, MessageQuote, Quote, User

# Set to true to get a verbose output
DEBUG = False

# Give an update per <UPDATE_MOD> messages processed
UPDATE_MOD = 100

"""
Class that abstracts away topic extraction
"""
class TopicExtractor(object):

	"""
	Returns all topics metioned in cleaned message version of argument 'message'
	This method now uses a java ner server to process requests which is much faster than calling java from python
	Need to make sure that the Java server is up and running on the speicified post
	"""
	def extract_topics(self, message, socket_to_tagger=ner.SocketNER(host='localhost', port=8070)):
		message_text = message.get_cleaned_post()
		res = socket_to_tagger.get_entities(message_text)
		named_entities = set()
		
		for (category, topics) in res.iteritems():
			# Iterate through topics found and add to return list
			for topic in topics:
				named_entities.add(topic)
				
		return named_entities

	"""
	Returns all the user mentions in the cleaned message version of argument 'message'
	"""
	def extract_user_mentions(self, message):
		message_text = message.get_cleaned_post()
		tokens = self.tokenizer.tokenize(message_text)	
		user_mentions = set()
		
		# Iterate through tokenized version of cleaned message looking for user mentioned
		for token in tokens:
			# User mentions begin with a '@'
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
	"""
	Note that there can be problems if the session we are using is not consistent 
	With the session connected to the message object passed in
	"""
	def extract_message_topic_to_db(self, message, db_session=None):
		
		# Defaults to stored session
		if db_session is None:
			db_session = self.session
		
		# Get topics and id for 'message' argument	
		topics = self.topic_extractor.extract_topics(message)
		message_id = message.get_message_id()
		
		# Iterate through all topics in the message
		for topic_str in topics:
			
			# Search topic table for topic
			topic_row = db_session.query(Topic).filter(Topic.topic == topic_str).first()
			topic_id = None
			
			# New topic, add & commit to database with initial count of 1 (message itself)
			if topic_row is None:
				new_topic = Topic(topic=topic_str, message_count=1)
				db_session.add(new_topic)
				db_session.commit()
				if DEBUG:
					print 'Adding new topic'
					print new_topic
				topic_id = new_topic.get_topic_id()
				
			# Existing topic entry, update table entry by incrementing message count
			else:
				topic_id = topic_row.get_topic_id()
				topic_row.increment_message_count()
				
			# Now we have to put corresponding entry in the message_topics table
			new_message_topic = MessageTopic(topic_id=topic_id, message_id=message_id)
			
			# Merge creates it or updates it if it already exists
			db_session.merge(new_message_topic)
			db_session.commit()

			if DEBUG:
				print 'Adding new message_topic : ', new_message_topic
				
	"""
	Runs the message topic extraction on a database iterator
	"""
	def run_topic_extraction(self, message_iterator=None, number_processed=0, total=100000, start_time=time.time()):
		
		# Default message_iterator argument
		# Set message_iterator to ForumMessage query, ordered on the message_id key
		if message_iterator is None:
			message_iterator = self.session.query(ForumMessage).order_by(ForumMessage.message_id)

		# Iterate through all message in message_iterator
		for msg in message_iterator:
			
			# Attempt to process message by extracting topics in try-catch block
			try:
				self.extract_message_topic_to_db(msg)
				number_processed += 1
				
				# Simple log to see how much progress we has been made
				if ((number_processed % UPDATE_MOD) == 0):
					elapsed_time = (time.time()-start_time)
					print "Processed : %i of %i in %s" % (number_processed, total, str(elapsed_time))
			
			# Catch all exceptions and print some debug text to diagnose error		
			except Exception as e:
				print "Exception message ", str(e)
				# rollback session
				self.session.rollback()


"""
Class for preprocessing and cleaning the message data
The pipepline for message cleaning is as follows:

Preprocesing Phase:
[ORIGINAL POST] -> quote_extraction -> mention_extraction -> forum_syntax_removal -> [CLEANED MESSAGE]

NLP Phase:
[CLEANED MESSAGE] -> topic_extraction -> sentiment_analysis
"""
class PreProcessing(object):

	# Note: this always grabs the outermost quote. So nested quotes wil be treated text in the outermost quote
	quote_regex_expr = r'(\[quote id=(?P<quote_id>([0-9-])+)\](?P<text>[\W\w]+)\[/quote\])+'
	quote_regex = re.compile(quote_regex_expr, re.IGNORECASE)
	users_regex_expr = r'@(?P<username>(\w)+)'
	users_regex = re.compile(users_regex_expr)
	forum_syntax_regex_expr = r'(\[\w+\]|\[/\w+\])*'
	forum_syntax_regex = re.compile(forum_syntax_regex_expr)
	
	def __init__(self, session=MySQLSession().get_session()):
		self.session = session

	def remove_quotes_from_message_to_db(self, message):
		# Here we run it on the original post
		# This is because quote extraction is first in the pipeline of pre-processing
		message_text = message.get_post()
		results = re.search(self.quote_regex, message_text)
		
		if results is not None:
			results_dictionary = results.groupdict()
			# Extract fields
			quote_id = results_dictionary['quote_id']
			quote_text = results_dictionary['text']
			# Clean the message by replacing the quote with the empty string
			cleaned_message_text = re.sub(self.quote_regex, '', message_text)
			# Set the cleaned message text
			message.set_cleaned_post(cleaned_message_text)
			# First tie the message to the quote
			message_quote = MessageQuote(quote_id=quote_id, message_id=message.get_message_id())
			self.session.merge(message_quote)
			# Then we need to find the quoted message
			quoted_message = self.session.query(ForumMessage) \
				.filter(ForumMessage.post.like('%'+quote_text+'%')) \
				.filter(ForumMessage.message_id != message.get_message_id()) \
				.first()
			quoted_message_id = None
			# Might not always be able to find it (e.g could be a quote from message not in the backing dataset)
			if quoted_message is not None:
				quoted_message_id = quoted_message.get_message_id()
			# Then add the quote
			quote = Quote(quote_id=quote_id, quote_text=quote_text, quoted_message_id=quoted_message_id)
			self.session.merge(quote)
			
		else:
			# Just use the original post
			message.set_cleaned_post(message.get_post())

		# Helpful debugger output
		if DEBUG:
			print "original message is : \n '%s' \n" % message_text
			print "with quote removed  : \n '%s' \n" % message.get_cleaned_post()
		
		self.session.commit()

	"""
	Runs quote extraction on database iterator using helper function remove_quotes_from_message_to_db
	"""
	def run_quotes_extraction(self, message_iterator, number_processed=0, total=100000, start_time=time.time()):
		# Iterate through all messages in database iterator
		for msg in message_iterator:
			
			# Attempt to run quote extraction on message
			try:
				self.remove_quotes_from_message_to_db(msg)
				number_processed += 1
				
				# Simple log to see how much progress we has been made
				if ((number_processed % UPDATE_MOD) == 0):
					elapsed_time = (time.time()-start_time)
					print "Processed : %i of %i in %s" % (number_processed, total, str(elapsed_time))
					
			# Catch all exceptions and print some debugging information
			except Exception as e:
				print "Exception message ", str(e)


	def extract_user_mentions_to_db(self, message, db_session=None):
		topic_extractor = TopicExtractor()
		message_text = message.get_cleaned_post()
		
	def clean_forum_snytax_from_message(self, message):
		# Here we are running it on the cleaned message
		# This is because in the chronology we extract quotes first and store the result in the cleaned post
		message_text = message.get_cleaned_post()
		cleaned_message_text = re.sub(self.forum_syntax_regex, '', message_text)
		message.set_cleaned_post(cleaned_message_text)

		# Helpful debugger output
		if DEBUG:
			print "original message is  : \n '%s' \n" % message_text
			print "without forum syntax : \n '%s' \n" % cleaned_message_text

		self.session.commit()


	"""
	Run forum syntax cleaning on database iterator using helper function clean_forum_snytax_from_message
	"""
	def run_forum_syntax_cleaning(self, message_iterator, number_processed=0, total=100000, start_time=time.time()):
		
		for msg in message_iterator:
			try:
				self.clean_forum_snytax_from_message(msg)
				number_processed += 1
				# Simple log to see how much progress we has been made
				if ((number_processed % UPDATE_MOD) == 0):
					elapsed_time = (time.time()-start_time)
					print "Processed : %i of %i in %s" % (number_processed, total, str(elapsed_time))
					
			except Exception as e:
				print "Exception message ", str(e)

	def extract_user_mentions_to_db(self, message):
		message_text = message.get_post()
		user_mentions = re.search(self.users_regex, message_text)
		message_id = message.get_message_id()

		for mentioned_user in user_mentions:
			# Extract fields
			mentions_dictionary = user_mentions.groupdict()
			mentioned_user = results_dictionary['username']

			# Query database for user mention
			user_row = self.session.query(User).filter(User.user == mentioned_user).first()
			user_id = None

			# No user_row in table - Create new user entry with count of 1 and commit to db
			if user_row is None:
				new_user = User(user = mentioned_user, user_count = 1)
				if DEBUG:
					print 'Add new user'
				self.session.add(new_user)
				self.session.commit()
				if DEBUG:
					print new_user
				user_id = new_user.get_user_id()
				
			# User_row entry already in table - update
			else:
				user_id = user_row.get_user_id()
				user_row.increment_user_count()

		# Remove the user mentions from the original message and store the clean message in the database
		cleaned_message_text = re.sub(self.users_regex, '', message_text)

		# Set the cleaned message text
		message.set_cleaned_post(cleaned_message_text)
		self.session.commit()

	"""
	Run user mentions extractions on database using helper function extract_user_mentions_to_db
	"""
	def run_user_mentions_extraction(self, message_iterator, number_processed=0, total=100000, start_time=time.time()):
		for msg in message_iterator:
			try:
				self.extract_user_mentions_to_db(msg)
				number_processed += 1
				# Simple log to see how much progress we has been made
				if ((number_processed % UPDATE_MOD) == 0):
					elapsed_time = (time.time()-start_time)
					print "Processed : %i of %i in %s" % (number_processed, total, str(elapsed_time))
			except Exception as e:
				print "Exception message ", str(e)
				
			try:
				self.extract_user_mentions_to_db(msg)
				number_processed += 1
				# Simple log to see how much progress we has been made
				if ((number_processed % UPDATE_MOD) == 0):
					elapsed_time = (time.time()-start_time)
					print "Processed : %i of %i in %s" % (number_processed, total, str(elapsed_time))
			except Exception as e:
				print "Exception message ", str(e)

class SentimentAnalysis(object):

	def __init__(self, session=MySQLSession().get_session(), sentiment_analyzer=NaiveBayesAnalyzer()):
		self.session = session
		self.sentiment_analyzer = sentiment_analyzer

	def extract_message_sentiment_to_db(self, message, db_session=None):
		# defaults to stored session
		if db_session is None:
			db_session = self.session
		sentiment = TextBlob(message.get_post()).sentiment.polarity;
		message_id = message.get_message_id()

		message.set_sentiment(sentiment);
		self.session.commit()

	"""
	Runs the snetiment analysis on a database iterator using helper function extract_message_sentiment_to_db
	"""
	def run_sentiment_analysis(self, message_iterator=None, number_processed=0, total=100000, start_time=time.time()):
		if message_iterator is None:
			message_iterator = self.session.query(ForumMessage).order_by(ForumMessage.message_id)

		for msg in message_iterator:
			try:
				self.extract_message_sentiment_to_db(msg)
				number_processed += 1
				# simple log to see how much progress we has been made
				if ((number_processed % UPDATE_MOD) == 0):
					elapsed_time = (time.time()-start_time)
					print "Processed : %i of %i in %s" % (number_processed, total, str(elapsed_time))
					
			except Exception as e:
				print "Exception message ", str(e)
				# rollback session
				self.session.rollback()

class Main(object):

	def run(self, quote_extraction=False, mention_extraction=False, forum_syntax_removal=False, topic_extraction=False, sentiment_analysis=False):

		print """PreProcessing Phase

		quote_extraction      : %s
		mention_extraction    : %s
		forum_syntax_removal : %s

		NLP Phase

		topic_extraction      : %s
		sentiment_analysis    : %s\n""" % (str(quote_extraction), str(mention_extraction), str(forum_syntax_removal), str(topic_extraction), str(sentiment_analysis))

		# remote version
		database_session = MySQLSession(username='cstkilo', password='Kilo_Jagex', host='localhost', port=3307,
			database='cstkilo').get_session()

		# local version
		# database_session = MySQLSession().get_session()

		# it's important here that all the methods are using the same database connection
		pre_processing = PreProcessing(session=database_session)
		processing = Processing(session=database_session)
		sentiment_analysis = SentimentAnalysis(session=database_session, sentiment_analyzer=NaiveBayesAnalyzer())

		"""
		Run quote, user mention, forum syntax removal, topic extraction and sentiment analysis as separate cases
		"""
		
		if quote_extraction:
			print "___________________________________________________\n"
			print "           Starting Quote Extraction               \n"
			print "___________________________________________________\n"

			# Split it into batches of 1000
			total = database_session.query(ForumMessage).count()
			number_processed = 0
			batch_size = 1000
			start_time = time.time()
			
			# process the batches one at a time
			while number_processed < total:
				pre_processing.run_quotes_extraction(
						database_session.query(ForumMessage)
							.order_by(ForumMessage.message_id).limit(batch_size).offset(number_processed),
						number_processed=number_processed,
						total=total,
						start_time=start_time)
				number_processed += batch_size

			print "___________________________________________________\n"
			print "           Finished Quote Extraction               \n"
			print "___________________________________________________\n"

		if mention_extraction:
			print "___________________________________________________\n"
			print "        Starting User Mention Extraction           \n"
			print "___________________________________________________\n"
			while number_processed < total:
				pre_processing.run_user_mentions_extraction(
						database_session.query(ForumMessage)
							.order_by(ForumMessage.message_id).limit(batch_size).offset(number_processed),
						number_processed=number_processed,
						total=total,
						start_time=start_time)
				number_processed += batch_size
			print "___________________________________________________\n"
			print "        Finished User Mention Extraction           \n"
			print "___________________________________________________\n"


		if forum_syntax_removal:
			print "___________________________________________________\n"
			print "         Starting Forum Syntax Cleaning            \n"
			print "___________________________________________________\n"

			# Split it into batches of 1000
			total = database_session.query(ForumMessage).count()
			number_processed = 0
			batch_size = 1000
			start_time = time.time()
			
			# Process the batches one at a time
			while number_processed < total:
				pre_processing.run_forum_syntax_cleaning(
						database_session.query(ForumMessage)
							.order_by(ForumMessage.message_id).limit(batch_size).offset(number_processed),
						number_processed=number_processed,
						total=total,
						start_time=start_time)
				number_processed += batch_size

			print "___________________________________________________\n"
			print "         Finished Forum Syntax Cleaning            \n"
			print "___________________________________________________\n"


		if topic_extraction:
			print "___________________________________________________\n"
			print "           Starting Topic Extraction               \n"
			print "___________________________________________________\n"

			# Split it into batches of 1000
			total = database_session.query(ForumMessage).count()
			number_processed = 0
			batch_size = 1000
			start_time = time.time()
			
			# Process the batches one at a time
			while number_processed < total:
				processing.run_topic_extraction(database_session.query(ForumMessage)
					.order_by(ForumMessage.message_id).limit(batch_size).offset(number_processed),
					number_processed=number_processed, total=total, start_time=start_time)
				number_processed += batch_size

			print "___________________________________________________\n"
			print "           Finished Topic Extraction               \n"
			print "___________________________________________________\n"

		if sentiment_analysis:
			print "___________________________________________________\n"
			print "          Starting Sentiment Analysis              \n"
			print "___________________________________________________\n"

			# Split it into batches of 1000
			total = database_session.query(ForumMessage).count()
			number_processed = 0
			batch_size = 1000
			start_time = time.time()
			
			# Process the batches one at a time
			while number_processed < total:
				sentiment_analysis.run_sentiment_analysis(database_session.query(ForumMessage)
					.order_by(ForumMessage.message_id).limit(batch_size).offset(number_processed),
					number_processed=number_processed, total=total, start_time=start_time)
				number_processed += batch_size
				pass
			print "___________________________________________________\n"
			print "          Finished Sentiment Analysis              \n"
			print "___________________________________________________\n"


# Run the main program
if __name__ == '__main__':
	Main().run(forum_syntax_removal=True)
