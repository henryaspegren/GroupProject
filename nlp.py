import os
from nltk.tag.stanford import StanfordNERTagger
from sql_client import MySQLSession, ForumMessage, MessageTopic, Topic
from nltk.tokenize import TweetTokenizer

NLP_ROOT = os.getcwd()+'/stanford-ner/'
# alternative: english.all.3class.distsim.crf.ser.gz
NER_CLASSIFIER = 'english.conll.4class.distsim.crf.ser.gz'


"""
Class that abstracts away topic extraction
"""
class TopicExtractor:

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


"""
Jobs and helper functions to process messages in db 
and add in the extracted topics 
"""
def process_message_to_db(session, message):
	topic_extractor = TopicExtractor()
	topics = topic_extractor.extract_topics(message)
	message_id = message.get_message_id()
	for topic_str in topics:
		# search topic table for topic
		topic_row = session.query(Topic).filter(Topic.topic == topic_str).first()
		topic_id = None
		# new topic
		if topic_row is None:
			new_topic = Topic(topic=topic_str, message_count=1)
			print 'Adding new topic'
			session.add(new_topic)
			session.commit()
			print new_topic
			topic_id = new_topic.get_topic_id()
		# existing topic entry
		else:
			topic_id = topic_row.get_topic_id()
			topic_row.increment_message_count() 
		# Now we have to put corresponding entry in the 
		# message_topics table
		message_topic = session.query(MessageTopic).filter((MessageTopic.topic_id == topic_id) and (MessageTopic.message_id == message_id)).first()
		# if no entry put one in
		if message_topic is None:
			print 'Adding new message_topic'
			new_message_topic = MessageTopic(topic_id=topic_id, message_id=message_id)
			session.add(new_message_topic)
			session.commit()
			print new_message_topic

def run_topic_extraction(session, message_iterator):
	for msg in message_iterator:
		process_message_to_db(session, msg)



"""
Example format of the job we will run:

# change these parameters based on which db you want to connect to
mysql_session = MySQLSession('root', 'password', 'localhost', 3306, 'kilo')
session = mysql_session.get_session()
it = session.query(ForumMessage).order_by(ForumMessage.message_id).limit(10)
run_topic_extraction(session, it)	
session.close()

"""

