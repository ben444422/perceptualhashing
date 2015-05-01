import sys
import hashlib
from collections import deque
from simhash import *


class FingerPrint:
	def __init__(self,hashes, k):
		self.hashes = hashes
		self.k = k

	def fingerprint(self):
		return self.hashes

class FingerPrinterSimHash:
	def __init__(self):
		pass		

	def fingerprints(self,document,k_len,win_len):
		# document = document.decode('utf-8')
		document = self._preprocess(document)
		kgrams = self._get_kgrams(document, k_len)

		hashes = [SimHashKGram(kgram,128,5).hash for kgram in kgrams]
		if win_len > len(hashes):
			win_len = len(hashes)

		fps = {}
		d = deque()
		for i in range(win_len):
			while len(d) != 0 and hashes[i] <= hashes[d[-1]]:
				d.pop()
			d.append(i)
		for i in range(win_len, len(hashes)):
			h = hashes[d[0]]
			if h in fps:
				fps[h].add(d[0])
			else:
				fps[h] = set([d[0]])

			while len(d) != 0 and d[0] <= i - win_len:
				d.popleft()

			while len(d) != 0 and hashes[i] <= hashes[d[-1]]:
				d.pop()

			d.append(i)

		h = hashes[d[0]]
		if h in fps:
			fps[h].add(d[0])
		else:
			fps[h] = set([d[0]])
		return FingerPrint(fps, k_len)

	def overlap_score(self, fingerprint1,fingerprint2, sim_thresh):
		fp1 = fingerprint1.fingerprint()
		fp2 = fingerprint2.fingerprint()
		if fingerprint1.k != fingerprint2.k:
			raise ValueError("The k grams lengths must be the same.")

		fps1 = set(fp1.keys())
		fps2 = set(fp2.keys())

		fps = fps1 if len(fps1) > len(fps2) else fps2
		fps_other = fps2 if len(fps1) > len(fps2) else fps1

		score = 0.
		for h in fps:
			for h2 in fps_other:
				sim = 1 - float((h ^ h2).count())/len(h)
				if sim > sim_thresh:
					score += 1.
					break
		return score/len(fps)


	def _get_kgrams(self,document, k_len):
		return [document[index:index+k_len] for index in range(len(document) - k_len + 1)]

	def _preprocess(self,document):
		document = "".join([word for word in document.lower().split()])
		return document

class FingerPrinter:
	def __init__(self):
		pass

	# use a winnowing algorithm
	def fingerprints(self, document, k_len, win_len):
		document = self._preprocess(document)
		kgrams = self._get_kgrams(document, k_len)

		hashes = [int(hashlib.md5(kgram.encode('utf-8')).digest().encode('hex'),16) for kgram in kgrams]
		fps = {}
		d = deque()
		
		if win_len > len(hashes):
			win_len = len(hashes)
			
		for i in range(win_len):
			while len(d) != 0 and hashes[i] <= hashes[d[-1]]:
				d.pop()
			d.append(i)
		for i in range(win_len, len(hashes)):
			h = hashes[d[0]]
			if h in fps:
				fps[h].add(d[0])
			else:
				fps[h] = set([d[0]])

			while len(d) != 0 and d[0] <= i - win_len:
				d.popleft()

			while len(d) != 0 and hashes[i] <= hashes[d[-1]]:
				d.pop()

			d.append(i)

		h = hashes[d[0]]
		if h in fps:
			fps[h].add(d[0])
		else:
			fps[h] = set([d[0]])
		return FingerPrint(fps, k_len)

	def overlap_score(self, fingerprint1,fingerprint2):
		fp1 = fingerprint1.fingerprint()
		fp2 = fingerprint2.fingerprint()
		if fingerprint1.k != fingerprint2.k:
			raise ValueError("The k grams lengths must be the same.")

		fps1 = set(fp1.keys())
		fps2 = set(fp2.keys())

		return float(len(set(fps1.intersection(fps2))))/ len(fps1.union(fps2)) 

	def intersection(self,fingerprint1,fingerprint2):
		s = []		
		fp1 = fingerprint1.fingerprint()
		fp2 = fingerprint2.fingerprint()
		for h in fp1:
			if h in fp2:
				s.append((h,fp1[h],fp2[h]))
		return s

	def _get_kgrams(self,document, k_len):
		return [document[index:index+k_len] for index in range(len(document) - k_len + 1)]

	def _preprocess(self,document):
		document = "".join([word for word in document.lower().split()])
		return document


if __name__ == "__main__":
	k_len = 40
	win_len = 5
	fpr = FingerPrinter()
	doc1 = """
	A hash function maps input data to output data of a fixed size. These functions are bit sensitive in that small changes to the input data drastically change the output. Perceptual hash functions are distinguished by the fact that small changes to the input lead to small changes to the output. Perceptual hashes are commonly used to fingerprint multimedia to detect possible copies. 
	"""
	doc2 = """
	As such, we can conclude that there is no systematic manner of accessing the true similarity between documents, A hash function maps input data to output data of a fixed size. so we must rely on some heuristic as an estimation of true similarity. I propose the following scheme. Generate a Document D' that is a percentage P different from a Document D by randomly selecting P percent of the words in D and replacing them with same length strings of random characters. This is a very basic method of generating a Document D' that is P\% different from D, but it allows for fine control over the value of P. An alternative is to grab documents, say from Wikipedia, and use a heuristic such as tf-idf to estimate similarity. However, there is little control over the value of P because finding a pair of documents with a specific P may require exhaustively searching through thousands of pairs of documents. 
	"""

	doc1n = "".join([word for word in doc1.lower().split()])
	doc2n = "".join([word for word in doc2.lower().split()])
	fp1 = fpr.fingerprints(doc1,k_len,win_len)
	fp2 = fpr.fingerprints(doc2,k_len,win_len)
	
	intersect = fpr.intersection(fp1,fp2)
	
	for h,s1,s2 in intersect:
		for i in s1:
			print i
			print doc1n[i:i+k_len]
	print fpr.overlap_score(fp1,fp2)




