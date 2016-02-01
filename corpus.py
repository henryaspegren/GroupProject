from nltk.data import LazyLoader
from nltk.tokenize import TreebankWordTokenizer
from nltk.util import AbstractLazySequence, LazyMap, LazyConcatenation
from nltk.probability import FreqDist
from nltk.corpus import stopwords

from sql_client import MySQLSession, ForumMessage

import pickle


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


"""
Generates a frequency dist from a corpus reader.
Saves it as a python pickled object in the given file
"""
def generate_frequency_dist(corpus_reader=MySQLDBCorpusReader(), file='freq_dist.pkl'):
	fdist = FreqDist(corpus_reader.words())
	with open(file,'wb') as f:
		pickle.dump(fdist, f)


"""
Loads a frequency distribution from a given pickle
file
"""
def load_frequency_dist(file='freq_dist.pkl'):
	with open('freq_dist.pkl', 'rb') as f:
		fdist = pickle.load(f)
	return fdist


# fdist1 = load_frequency_dist()
# stop = stopwords.words('english')
# words = fdist1.most_common(1000)
# for (word, count) in words:
# 	if word not in stop and len(word) > 8:
# 		print "'%s' : '%i'" % (word, count)


# a = MySQLDBLazySequence()

# iterator = a.iterate_from(0)

# i = 0 
# for message in iterator:
# 	i += 1
# 	if i > 20:
# 		break
# 	print message