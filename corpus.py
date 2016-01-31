from nltk.data import LazyLoader
from nltk.tokenize import TreebankWordTokenizer
from nltk.util import AbstractLazySequence, LazyMap, LazyConcatenation
from sql_client import MySQLSession, ForumMessage


"""
A Lazy iterator for data stored in a MySQL 
database rather than having to load it into memory
"""
class MySQLDBLazySequence(AbstractLazySequence):

	def __init__(self, mysqlsession=MySQLSession(), table_column=ForumMessage.post, 
			order_by=ForumMessage.message_id):
		self.session = mysqlsession.get_session()
		self.table_column = table_column
		self.order_by = order_by

	def __len__(self):
		return self.session.query(self.table_column).count()

	def iterate_from(self, start):
		# just grabs the first element of the tuple returned 
		f = lambda x : x[0]
		return iter(LazyMap(f, self.session.query(self.table_column).order_by(self.order_by).offset(start)))

"""
Corpus reader for a MySQL database. Allows
for NLTK analysis without having to 
store text files locally.
"""
class MySQLDBCorpusReader(object):

	def __init__(self, word_tokenizer=TreebankWordTokenizer(), 
			sent_tokenizer=LazyLoader('tokenizers/punkt/english.pickle'),
			**kwargs):
		self._word_tokenizer = word_tokenizer.tokenize
		self._sent_tokenizer = sent_tokenizer.tokenize
		self._sequence = MySQLDBLazySequence(**kwargs)

		 
	def text(self):
		return self._sequence

	def words(self):
		return LazyConcatenation(LazyMap(self._word_tokenizer, self.text()))

	def sents(self):
		return LazyConcatenation(LazyMap(self._sent_tokenizer, self.text()))

