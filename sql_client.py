from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class MySQLSession:

	def __init__(self, username, passowrd, host, port, database):
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


class ForumMessage(Base):
	__tablename__ = 'forum_messages'
	message_id = Column(Integer, primary_key=True)
	user_id = Column(Integer)
	time_stamp = Column(String)
	forum_name = Column(String)
	post = Column(String)

	def __repr__(self):
		return "<ForumMessage(message_id='%i', user_id='%i', time_stamp='%s' \
			forum_name='%s')>" % (self.message_id, self.user_id, self.time_stamp, self.forum_name)


mysql_session = MySQLSession('root', 'password', 'localhost', 3306, 'kilo')
session = mysql_session.get_session()

i = 0
for instance in session.query(ForumMessage).order_by(ForumMessage.message_id):
	i += 1
	print instance
	if i > 10:
		break
