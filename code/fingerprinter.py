import sys
import hashlib
from collections import deque


class FingerPrint:
	def __init__(self,hashes):
		self.hashes = hashes

	def fingerprint(self):
		return self.hashes

class FingerPrinter:
	def __init__(self, k_length, window_length):
		self.k = k_length
		self.window_length = window_length

	# use a winnowing algorithm
	def fingerprints(self, document):
		document = self._preprocess(document)
		kgrams = self._get_kgrams(document)

		hashes = [int(hashlib.md5(kgram).digest().encode('hex'),16) for kgram in kgrams]
		fps = []
		d = deque()
		for i in range(self.window_length):
			while len(d) != 0 and hashes[i] <= hashes[d[-1]]:
				d.pop()
			d.append(i)
		for i in range(self.window_length, len(hashes)):
			fps.append((hashes[d[0]],d[0]))
			while len(d) != 0 and d[0] <= i - self.window_length:
				d.popleft()

			while len(d) != 0 and hashes[i] <= hashes[d[-1]]:
				d.pop()

			d.append(i)

		fps.append(hashes[d[0]])
		return FingerPrint(set(fps))

	def similarity(self,fingerprint1,fingerprint2):
		return float(len(fingerprint1.intersection(fingerprint2)))/len(fingerprint1.union(fingerprint2))




	def _get_kgrams(self,document):
		return [document[index:index+self.k] for index in range(len(document) - self.k + 1)]

	def _preprocess(self,document):
		document = "".join([word for word in document.lower().split()])
		return document

if __name__ == "__main__":
	fpr = FingerPrinter(5,5)
	doc1 = "this is my name, and it is ben."
	doc2 = "this is my nme, and it is ."
	fp1 = fpr.fingerprints(doc1).fingerprint()
	fp2 = fpr.fingerprints(doc2).fingerprint()
	print fpr.similarity(fp1,fp2)





