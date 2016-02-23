from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# common base class. 
# needs to be shared among all tables for foreign key to work
Base = declarative_base()

"""
Represents a connection to a MYSQL database.
"""
class MySQLSession(object):
	def __init__(self, username='cstkilo', password='Kilo_Jagex', host='localhost', port=3307,
			database='cstkilo'):
		self.username = username
		self.password = password
		self.host = host
		self.port = port
		self.database = database

		# format: dialect+driver://username:password@host:port/database
		self.engine = create_engine('mysql+pymysql://'+self.username+":"+self.password \
			+"@"+self.host+":"+str(self.port)+"/"+self.database)

	def get_engine(self):
		return self.engine

	def get_session(self):
		Session = sessionmaker(bind=self.engine)
		return Session()


"""
Basic wrapper class for the forum messages data table. 
It's python object that allows you to interact with entries.

"""
class ForumMessage(Base):
	__tablename__ = 'forum_messages'
	
	"""
	Each forum message has 7 fields:
		message_id, user_id, time_stamp, forum_name, post, cleaned_post, sentiment
	message_id used to uniquely identify records in forum message table
	"""
	
	message_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
	user_id = Column(Integer)
	time_stamp = Column(String)
	forum_name = Column(String)
	post = Column(String)
	# to store the 'cleaned' pre-processed version of the post text
	cleaned_post = Column(String)
	# to store sentiment
	sentiment = Column(Float)

	# returns representation of table entry as a ForumMessage object
	def __repr__(self):
		return "<ForumMessage(message_id='%i', user_id='%i', time_stamp='%s', forum_name='%s')>" % (self.message_id, self.user_id, self.time_stamp, self.forum_name)
	
	"""
	Simple getter functions
	"""
	
	def get_message_id(self):
		return self.message_id

	def get_user_id(self):
		return self.user_id

	def get_forum_name(self):
		return self.forum_name

	def get_post(self):
		return self.post

	def get_cleaned_post(self):
		return self.cleaned_post

	def get_sentiment(self):
		return self.sentiment

	"""
	Simple setter functions for two fields: cleaned_post and sentiment
	"""
	
	def set_cleaned_post(self, cleaned_text):
		self.cleaned_post = cleaned_text

	def set_sentiment(self, sentiment):
		self.sentiment = sentiment

	# use this for serialization in the API
	def to_json(self):
		return {'message_id':self.message_id, 'user_id':self.user_id, 'forum_name': self.forum_name, 'post':self.cleaned_post, 'sentiment' : self.sentiment}


"""
ORM for the Topic database
"""
class Topic(Base):
	__tablename__ = 'topics'
	
	"""
	Each topic entry has 3 fields:
		topic_id, topic, message
	topic_id used to uniquely identify each record in table (possibly set to None)
	"""
	
	topic_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
	topic = Column(String)
	message_count = Column(Integer)

	# returns representation of table entry as a Topic object
	def __repr__(self):
		if self.topic_id is None:
			return "<Topic(topic_id='NA', topic='%s', message_count='%i')>" % (self.topic, self.message_count)
		else:
			return "<Topic(topic_id='%i', topic='%s', message_count='%i')>" % (self.topic_id, self.topic, self.message_count)

	def to_json(self):
		return {'topic': self.topic, 'topic_id' : self.topic_id, 'message_count': self.message_count}
		
	def increment_message_count(self):
		self.message_count += 1
	"""
	Simple getter functions
	"""
	
	def get_topic_id(self):
		return self.topic_id

	def get_topic(self):
		return self.topic

	def get_message_count(self):
		return self.message_count


"""
ORM for the Message Topics 
"""
class MessageTopic(Base):
	__tablename__ = 'message_topics'
	
	"""
	Each MessageTopic entry has 2 fields:
		topic_id, message_id
	topic_id used as key into table
	"""
	
	topic_id = Column(Integer, ForeignKey("topics.topic_id"), primary_key=True, nullable=False)
	message_id = Column(Integer, ForeignKey("forum_messages.message_id"), primary_key=True, nullable=False)

	# returns representation of table entry as a MessageTopic object
	def __repr__(self):
		return "<MessageTopic(topic_id='%i', message_id='%i')>" % (self.topic_id, self.message_id)

	"""
	Simple getter functions
	"""
	
	def get_topic_id(self):
		return self.topic_id

	def get_message_id(self):
		return self.message_id

""" 
ORM for the Quote database
"""
class Quote(Base):
	__tablename__ = 'quotes'
	
	"""
	Each table entry has 3 fields:
		quote_id, quote_text, quoted_message_id
	quote_id used as key into table
	"""
	
	quote_id = Column(String, primary_key=True, nullable=False, unique=True)
	quote_text = Column(String, nullable=False)
	quoted_message_id = Column(Integer, ForeignKey("forum_messages.message_id"), nullable=True)

	# returns representation of table entry as a Quote object
	def __repr__(self):
		return "<Quote(quote_id='%s', quote_text='%s')>" % (self.quote_id, self.quote_text)

	"""
	Simple getter functions
	"""
	
	def get_quote_id(self):
		return self.quote_id

	def get_quote_text(self):
		return self.quote_text

	""" 
	Simple setter functions
	"""
	
	def set_quote_text(self, new_quote_text):
		self.quote_text = new_quote_text

	def get_quoted_message_id(self):
		return self.quoted_message_id

	def set_quoted_message_id(self, quoted_message_id):
		self.quoted_message_id = quoted_message_id 

"""
ORM for the Message Quotes
"""
class MessageQuote(Base):
	__tablename__ = 'message_quotes'
	quote_id = Column(String, primary_key=True, nullable=False)
	message_id = Column(Integer, ForeignKey("forum_messages.message_id"), primary_key=True, nullable=False)

	def __repr__(self):
		return "<MessageQuote(quote_id='%s', message_id='%i')>" % (self.quote_id, self.message_id)

	def get_quote_id(self):
		return self.quote_id

	def get_message_id(self):
		return self.message_id


"""
ORM for the User database
"""
class User(Base):
	__tablename__ = 'users'
	
	"""
	Each entry has 3 fields:
		user_id, user, user_count
	user_id used as key into table
	"""
	
	user_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
	user = Column(String)
	user_count = Column(Integer)

	# returns representation of table entry as a User object
	def __repr__(self):
		if self.user_id is None:
			return "<User(user_id='NA', user='%s')>" % (self.user)
		else:
			return "<User(user_id='%i', user='%s')>" % (self.user_id, self.user)

	def increment_user_count(self):
		self.user_count += 1
		
	"""
	Simple getter functions
	"""
	
	def get_user_id(self):
		return self.user_id

	def get_user(self):
		return self.user

	def get_user_count(self):
		return self.user_count
