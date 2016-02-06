from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# common base class. 
# needs to be shared among all tables for foreign key to work
Base = declarative_base()

"""
Represents a connection to a MYSQL database.
"""
class MySQLSession(object):
	def __init__(self, username='root', passowrd='password', host='localhost', port=3306, 
			database='kilo'):
		self.username = username
		self.passowrd = passowrd
		self.host = host
		self.port = port
		self.database = database

		# format: dialect+driver://username:password@host:port/database
		self.engine = create_engine('mysql+pymysql://'+self.username+":"+self.passowrd \
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
	message_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
	user_id = Column(Integer)
	time_stamp = Column(String)
	forum_name = Column(String)
	post = Column(String)
	# to store the 'cleaned' pre-processed version of the post text
	cleaned_post = Column(String)

	def __repr__(self):
		return "<ForumMessage(message_id='%i', user_id='%i', time_stamp='%s', forum_name='%s')>" % (self.message_id, self.user_id, self.time_stamp, self.forum_name)
	
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

	def set_cleaned_post(self, cleaned_text):
		self.cleaned_post = cleaned_text

	# use this for serialization in the API
	def to_json(self):
		return {'message_id':self.message_id, 'user_id':self.user_id, 'forum_name': self.forum_name, 'post':self.post}


"""
ORM for the Topic database
"""
class Topic(Base):
	__tablename__ = 'topics'
	topic_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
	topic = Column(String)
	message_count = Column(Integer)

	def __repr__(self):
		if self.topic_id is None:
			return "<Topic(topic_id='NA', topic='%s', message_count='%i')>" % (self.topic, self.message_count)
		else:
			return "<Topic(topic_id='%i', topic='%s', message_count='%i')>" % (self.topic_id, self.topic, self.message_count)

	def to_json(self):
		return {'topic': self.topic, 'topic_id' : self.topic_id, 'message_count': self.message_count}

	def get_topic_id(self):
		return self.topic_id

	def get_topic(self):
		return self.topic

	def get_message_count(self):
		return self.message_count

	def increment_message_count(self):
		self.message_count += 1


"""
ORM for the Message Topics 
"""
class MessageTopic(Base):
	__tablename__ = 'message_topics'
	topic_id = Column(Integer, ForeignKey("topics.topic_id"), primary_key=True, nullable=False)
	message_id = Column(Integer, ForeignKey("forum_messages.message_id"), primary_key=True, nullable=False)

	def __repr__(self):
		return "<MessageTopic(topic_id='%i', message_id='%i')>" % (self.topic_id, self.message_id)

	def get_topic_id(self):
		return self.topic_id

	def get_message_id(self):
		return self.message_id

""" 
ORM for the Quote database
"""
class Quote(Base):
	__tablename__ = 'quotes'
	quote_id = Column(String, primary_key=True, nullable=False, unique=True)
	quote_text = Column(String, nullable=False)

	def __repr__(self):
		return "<Quote(quote_id='%s', quote_text='%s')>" % (self.quote_id, self.quote_text)

	def get_quote_id(self):
		return self.quote_id

	def get_quote_text(self):
		return self.quote_text

	def set_quote_text(self, new_quote_text):
		self.quote_text = new_quote_text

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