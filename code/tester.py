from simhash import *
from docsim import DocSim
from util import DocumentSet
import sys
import operator
import random
import string
import time

class TestHouse:
	def __init__(self, docSet):
		self.document_set = docSet
		self.documents = docSet.documents
		self.doc_list = [title for title,body in self.documents.items()]	


	# Use tf-idf as a bench mark. create random triples of documents (1,2,3) 
	# use tf idf with cosine similarity to test whether 1 is more similar to 2 or 3
	# see if SimHash gives the same result. 
	def compare_algs_tfidf_simhash(self):
		token_length = 1
		test_set = self.generate_random_triples()
		simhash_dict = {}

		for title in self.doc_list:
			simhash_dict[title] = SimHash(self.documents[title], 128, token_length)

		ds = DocSim(self.document_set)

		total = float(len(test_set))
		correct= 0.
		for t1,t2,t3 in test_set:
			dsim1 = ds.sim(t1,t2)
			dsim2 = ds.sim(t1,t3)
			ssim1 = simhash_dict[t1].similarity(simhash_dict[t2])
			ssim2 = simhash_dict[t1].similarity(simhash_dict[t3])
			if (abs(dsim1 - 0) < 0.000001 and abs(dsim2 - 0) < 0.000001):
				total -= 1.
				continue
			db = dsim1 < dsim2
			sb = ssim1 < ssim2
			
			if db == sb:
				correct += 1.
		return correct/total

	# compare docsim with SimHashTfIdf
	def compare_algs_tfidf_simhashtfidf(self):
		token_length = 1
		test_set = self.generate_random_triples()

		ds = DocSim(self.document_set)
		sh = SimHashTfIdf(self.document_set)

		total = float(len(test_set))
		correct= 0.
		for t1,t2,t3 in test_set:
			dsim1 = ds.similarity(t1,t2)
			dsim2 = ds.similarity(t1,t3)
			ssim1 = sh.similarity(t1,t2)
			ssim2 = sh.similarity(t1,t3)

			if ((abs(dsim1 - 0) < 0.000001 and abs(dsim2 - 0) < 0.000001)):
				total -= 1.
				continue
			db = dsim1 < dsim2
			sb = ssim1 < ssim2
			
			if db == sb:
				correct += 1.
		# print len(test_set)
		# print total
		return correct/total


	# test effectiveness of simhash when documents are artificially modified
	def compare_simhash_replace(self, iterations, hash_length):
		token_length = 3
		REPLACEMENT_LIMIT = 1.0
		correct = 0.

		for x in range(iterations):

			rand_doc = self.document_set.get_random_document()
			title,body = rand_doc
			body = self.documents[title]
			ratio1 = random.random()*REPLACEMENT_LIMIT 
			ratio2 = random.random()*REPLACEMENT_LIMIT

			shorter = ratio1 if ratio1 < ratio2 else ratio2
			longer = ratio2 if ratio1 < ratio2 else ratio1

			doc1 = self.replace(body,shorter)
			doc2 = self.replace(body,longer)

			hash1 = SimHash(body,hash_length,token_length)
			hash2 = SimHash(doc1,hash_length,token_length)
			hash3 = SimHash(doc2,hash_length,token_length)

			if hash1.similarity(hash2) > hash1.similarity(hash3):
				correct += 1.

		return correct/iterations

	# test effectiveness of tf-idf when documents are artificially modified
	def compare_tfidf_replace(self, iterations):
		token_length = 1
		REPLACEMENT_LIMIT = 1.0
		ds = DocSim(self.document_set)
		correct = 0.
		for x in range(iterations):
			rand_doc = self.document_set.get_random_document()
			ratio1 = random.random()*REPLACEMENT_LIMIT 
			ratio2 = random.random()*REPLACEMENT_LIMIT
			shorter = ratio1 if ratio1 < ratio2 else ratio2
			longer = ratio2 if ratio1 < ratio2 else ratio1

			body1 = self.replace(rand_doc[1],shorter)
			body2 = self.replace(rand_doc[1],longer)

			sim1 = ds.similarity_new_doc(rand_doc[0],body1)
			sim2 = ds.similarity_new_doc(rand_doc[0],body2)

			if sim1 > sim2:
				correct += 1.
		return correct/iterations

	def select_random_document(self):
		return random.choice(self.doc_list)

	def generate_random_triples(self):
		l1 = list(self.doc_list)
		l2 = list(self.doc_list)
		l3 = list(self.doc_list)
		random.shuffle(l1)
		random.shuffle(l2)
		random.shuffle(l3)
		return zip(l1,l2,l3)

	def test_document_similarity(self):
		random_document = self.document_set.get_random_document()
		print "Random Document: " + random_document[0]
		print "Random Document Body: " + random_document[1]
		h1 = SimHash(random_document[1], 128, 1)
		doc_sims = []
		for title in self.documents:
			text = self.documents[title]
			h2 = SimHash(text,128,1)
			sim = h1.similarity(h2)
			print title + ": " + str(sim)
			doc_sims.append((title,sim))
		print "\n".join([str(i[0]) + ": " + str(i[1]) for i in sorted(doc_sims, key = lambda tup : tup[1])])


	def benchmark_simhash(self, iterations, hash_length, token_length):
		t0 = time.clock()
		simhashes = {}
		for i in range(iterations):
			title1 = self.select_random_document()
			title2 = self.select_random_document()
			if title1 not in simhashes:
				simhashes[title1] = SimHash(self.documents[title1],hash_length,token_length)
			if title2 not in simhashes:
				simhashes[title2] = SimHash(self.documents[title2],hash_length,token_length)
			sh1 = simhashes[title1]
			sh2 = simhashes[title2]
			sim = sh1.similarity(sh2)
		t1 = time.clock()
		span = t1 - t0
		print "Running " + str(iterations) + " iterations took " +  str(span) + " microseconds"



			




	def test_random_change_range(self, change_type, token_length, percentage_change_start, percentage_change_interval, num_runs):
		for i in range(num_runs):
			p = percentage_change_start + percentage_change_interval*i
			tot = 0.0
			for title in self.documents:
				text = self.documents[title]
			 	sim = self.test_similarity(text,change_type,token_length,p)
			 	tot += sim
			avg = tot / (len(self.documents))
			print str(p) + "\t" + str(avg) 		



	def test_random_strings(self, length,word_length, num_runs):
		tot = 0.
		for i in range(num_runs):
			str1 = self.generate_random_string(length,word_length)
			str2 = self.generate_random_string(length,word_length)
			h1 = SimHash(str1, 128, 1)
			h2 = SimHash(str2, 128, 1)
			tot += h1.similarity(h2)
		return tot/num_runs


	def test_random_change(self, change_type, token_length, percentage_change):
		for title in self.documents:
			text = self.documents[title]
			print title + " " + str(self.test_similarity(text,change_type,token_length,percentage_change))

	def test_similarity(self, text, change_type, token_length, percentage_change):
		text_mod = ""
		if change_type == "replace":
			text_mod = self.replace(text,percentage_change)
		elif change_type == "permute":
			text_mod = self.permute(text, percentage_change)
		else:
			raise Exception("Invalid document change type")
		h1 = SimHash(text,128, token_length)
		h2 = SimHash(text_mod,128, token_length)
		return h1.similarity(h2)

	def replace(self, document, percentage_change):
		num_changes = int(len(document)*percentage_change)
		
		indices = set(random.sample(range(len(document)), num_changes))
		new_doc = ""
		for i in range(len(document)):
			if i in indices:
				new_doc += random.choice(string.ascii_letters)
			else:
				new_doc += document[i]
		return new_doc

	def permute(self, document, percentage_change):
		words = document.split()
		num_changes = int(len(words)*percentage_change)
		indices = random.sample(range(len(words)), num_changes)
		indices2 = random.sample(range(len(words)), num_changes)
		for i,j in zip(indices,indices2):
			w = words[i]
			words[i] = words[j]
			words[j] = w
		return " ".join(words)

	def generate_random_string(self, length, word_length):
		st = ""
		for i in range(length):
			st += random.choice(string.ascii_letters)
			if random.randint(0,word_length) == 1:
				st += " "
		return st
		
if __name__ == "__main__":
	ds = DocumentSet()
	th = TestHouse(ds)

	#th.benchmark_simhash(100, 128,1)


	# testing the accuracy of simhash by modifying a document twice and seeing which version is more similar
	print th.compare_simhash_replace(100, 128)
	
	# # Seeing how the accuracy of SimHash changes as the hash length changes
	# for i in range(16,128):
	# 	print str(i) + ": " + str(th.compare_simhash_replace(100, i))


	# print th.compare_tfidf_replace(100)


	#th.compare_algs_tfidf_simhash()
	# for i in range(20,1000)[0::10]:
	# 	print str(i) + "\t" + str(th.test_random_strings(i,5,50))

	#h1 = SimHash("text this is not",128, 1)
	#h2 = SimHash("hi blue ben",128, 1)
	#print h1.similarity(h2)
	# th.test_document_similarity()
#	th.test_random_change("replace", 1, 0.01)
#	th.test_random_change_range("replace",1,0.0,0.01,100)

	#dsim = DocSim(ds)

	#shtfidf = SimHashTfIdf(ds)






