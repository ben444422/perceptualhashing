import hashlib
import sys
from nltk.corpus import stopwords
from bitarray import bitarray
from nltk.stem.snowball import EnglishStemmer
from gensim import corpora, models, similarities
import random

class SimHashTfIdf:
	MAX_HASH_LENGTH = 128

	def __init__(self, doc_set, hash_length = 32, words_per_token = 1):
		if hash_length > self.MAX_HASH_LENGTH:
			raise Exception("The specified hash length is too long. It must be 128 bits or less")
		self.hash_length = hash_length
		self.documents = doc_set.documents
		docs = [title + " " + body for title,body in self.documents.items()]
		self.doc_list = [title for title,body in self.documents.items()]	
		self.inverted_doc_index = {}
		for index,title in enumerate(self.doc_list):
			self.inverted_doc_index[title] = index
		texts = [[word for word in document.lower().split() if word not in stopwords.words('english')] for document in docs]
		self.dictionary = corpora.Dictionary(texts)
		self.corpus = [self.dictionary.doc2bow(text) for text in texts] 
		self.tfidf = models.TfidfModel(self.corpus)
		self.index = similarities.SparseMatrixSimilarity(self.tfidf[self.corpus], num_features=len(self.dictionary))
		self.simhash_dict = {}

		for ind,v in enumerate(self.corpus):
			self.simhash_dict[self.doc_list[ind]] = self.create_hash(self.tfidf[v])

		# l1 = list(self.doc_list)
		# l2 = list(self.doc_list)
		# random.shuffle(l1)
		# random.shuffle(l2)
		# pairs = zip(l1,l2)
		# tot = 0.
		# for t1,t2 in pairs:
		# 	sim = self.similarity(t1,t2)
		# 	print sim
		# 	tot += sim

		# print tot / len(pairs)


	def create_hash(self, vec):
		v = [0.]*self.hash_length
		for ind,weight in vec:
			h = hashlib.md5()
			h.update(self.dictionary[ind])
			bytes = map(ord,h.digest())
			for i in range(0,self.hash_length):
				if self.get_bit(bytes,i) == 0:
					v[i] += weight
				else:
					v[i] -= weight
		return bitarray([True if c > 0. else False for c in v])

	# given a bytes array and an index, returns the bit at the specified index
	def get_bit(self,bytes,index):
		# first grab the specified byte
		byteIndex = index/8
		bitIndex = index % 8
		if byteIndex >= len(bytes):
			raise Exception("The index is too large")
		return 0 if bytes[byteIndex]&(2**bitIndex) != 0 else 1
	
	def similarity(self,title1,title2):
		if title1 not in self.simhash_dict or title2 not in self.simhash_dict:
			raise ValueError("Simhash doesn't exist")
		sh1 = self.simhash_dict[title1]
		sh2 = self.simhash_dict[title2]
		if len(sh1) != len(sh2):
			raise Exception("SimHashes must be of the same length to compare.")
		sim = 1 - float((sh1 ^ sh2).count())/len(sh1)
		return sim


class SimHashKGram:
	MAX_HASH_LENGTH = 128

	def __init__(self, text, hash_length = 32, k = 5):
		if hash_length > self.MAX_HASH_LENGTH:
			raise Exception("The specified hash length is too long. It must be 128 bits or less")
		if len(text) == 0:
			raise Exception("Document is empty")

		self.hash_length = hash_length
		self.words = self.process_text(text, k)
		self.hash = self.get_hash()
	
	def get_hash(self):
		v = [0]*self.hash_length
		for w in self.words:
			h = hashlib.md5()
			h.update(w.encode('utf-8'))
			bytes = map(ord,h.digest())
			for i in range(0,self.hash_length):
				if self.get_bit(bytes,i) == 0:
					v[i] += 1
				else:
					v[i] -= 1
		#return [True if c > 0 else False for c in v]
		return bitarray([True if c > 0 else False for c in v])

	# given a bytes array and an index, returns the bit at the specified index
	def get_bit(self,bytes,index):
		# first grab the specified byte
		byteIndex = index/8
		bitIndex = index % 8
		if byteIndex >= len(bytes):
			raise Exception("The index is too large")
		return 0 if bytes[byteIndex]&(2**bitIndex) != 0 else 1

	def process_text(self,text, k):
		es = EnglishStemmer()
		doc = "".join([es.stem(w.lower()) for w in text.split() if w.lower() not in (stopwords.words('english'))])
		return [doc[index:index+k] for index in range(len(doc) - k + 1)]
		


	# returns a float in the range 0 to 1 inclusive that indicates how
	# similar this simhash is to another simhash. 1 indicates complete similarity.
	# Complete dissimilarity falls in the range [0 - 0.5] because two randomly generated
	# bit strings will have an average dissimilarity ratio of 0.5 (roughly half of the bits
	# will match up)
	def similarity(self,otherHash):
		if len(self.hash) != len(otherHash.hash):
			raise Exception("SimHashes must be of the same length to compare.")
		sim = 1 - float((self.hash ^ otherHash.hash).count())/len(self.hash)
		return sim
	
	def __str__(self):
		return str(self.hash)


class SimHash: 
	MAX_HASH_LENGTH = 512

	def __init__(self, text, hash_length = 32, words_per_token = 1):
		if hash_length > self.MAX_HASH_LENGTH:
			raise Exception("The specified hash length is too long. It must be 128 bits or less")
		if len(text) == 0:
			raise Exception("Document is empty")

		self.hash_length = hash_length
		self.words = self.process_text(text, words_per_token)
		self.hash = self.get_hash()
	
	def get_hash(self):
		v = [0]*self.hash_length
		for w in self.words:
			h = hashlib.sha512()
			h.update(w.encode('utf-8'))
			bytes = map(ord,h.digest())
			for i in range(0,self.hash_length):
				if self.get_bit(bytes,i) == 0:
					v[i] += 1
				else:
					v[i] -= 1
		#return [True if c > 0 else False for c in v]
		return bitarray([True if c > 0 else False for c in v])

	# given a bytes array and an index, returns the bit at the specified index
	def get_bit(self,bytes,index):
		# first grab the specified byte
		byteIndex = index/8
		bitIndex = index % 8
		if byteIndex >= len(bytes):
			raise Exception("The index is too large")
		return 0 if bytes[byteIndex]&(2**bitIndex) != 0 else 1

	def process_text(self,text, words_per_token):
		es = EnglishStemmer()
		tokens = [es.stem(w.lower()) for w in text.split() if w.lower() not in (stopwords.words('english'))] 
		return [" ".join(tokens[words_per_token*i: words_per_token*i + words_per_token]) for i in range(int(len(tokens)/words_per_token))]


	# returns a float in the range 0 to 1 inclusive that indicates how
	# similar this simhash is to another simhash. 1 indicates complete similarity.
	# Complete dissimilarity falls in the range [0 - 0.5] because two randomly generated
	# bit strings will have an average dissimilarity ratio of 0.5 (roughly half of the bits
	# will match up)
	def similarity(self,otherHash):
		if len(self.hash) != len(otherHash.hash):
			raise Exception("SimHashes must be of the same length to compare.")
		sim = 1 - float((self.hash ^ otherHash.hash).count())/len(self.hash)
		return sim
	
	def __str__(self):
		return str(self.hash)

if __name__ == "__main__":
	h1 = SimHash("the Cat in the hat", 128)
	h2 = SimHash("ben is really cool", 128)
	print h1.similarity(h2)