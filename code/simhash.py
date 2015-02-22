import hashlib
import sys
from nltk.corpus import stopwords

class SimHash: 
	MAX_HASH_LENGTH = 128

	def __init__(self, text, hash_length = 32, words_per_token = 1):
		if hash_length > self.MAX_HASH_LENGTH:
			raise Exception("The specified hash length is too long. It must be 128 bits or less")
		self.hash_length = hash_length
		self.words = self.process_text(text, words_per_token)
		self.hash = self.get_hash()
	
	def get_hash(self):
		v = [0]*self.hash_length
		for w in self.words:
			h = hashlib.md5()
			h.update(w)
			bytes = map(ord,h.hexdigest())
			for i in range(0,self.hash_length):
				if self.get_bit(bytes,i) == 0:
					v[i] += 1
				else:
					v[i] -= 1
		return [1 if c > 0 else 0 for c in v]


	# given a bytes array and an index, returns the bit at the specified index
	def get_bit(self,bytes,index):
		# first grab the specified byte
		byteIndex = index/8
		bitIndex = index % 8
		if byteIndex >= len(bytes):
			raise Exception("The index is too large")
		return 0 if bytes[byteIndex]&(2**bitIndex) != 0 else 1

	def process_text(self,text, words_per_token):
		tokens = [w.lower() for w in text.split() if w.lower() not in (stopwords.words('english'))] 
		return [" ".join(tokens[words_per_token*i: words_per_token*i + words_per_token]) for i in range(len(tokens)/words_per_token)]


	# returns a float in the range 0 to 1 inclusive that indicates how
	# similar this simhash is to another simhash. 1 indicates complete
	# similarity and 0 indicates complete dissimilarity.
	def similarity(self,otherHash):
		if len(self.hash) != len(otherHash.hash):
			raise Exception("SimHashes must be of the same length to compare.")
		sim = 1. - float(sum(b1 != b2 for b1,b2 in zip(self.hash,otherHash.hash)))/float(len(self.hash))
		return 0. if sim < 0.5 else (sim - 0.5)/0.5

	def __str__(self):
		return ", ".join(map(str, self.hash))


if __name__ == "__main__":
	h1 = SimHash("the Cat in the hat", 128)
	h2 = SimHash("ben is really cool", 128)
	print h1.similarity(h2)