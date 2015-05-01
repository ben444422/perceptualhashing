from simhash import *
from fingerprinter import *
from docsim import DocSim
from util import DocumentSet
import sys
import operator
import random
import string
import time
import math
import resource


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


	def compare_simhashkgram_replace(self,iterations,hash_length,k):
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

			hash1 = SimHashKGram(body,hash_length,k)
			hash2 = SimHashKGram(doc1,hash_length,k)
			hash3 = SimHashKGram(doc2,hash_length,k)

			if hash1.similarity(hash2) > hash1.similarity(hash3):
				correct += 1.

		return correct/iterations

	def temp(self, iterations, win_len):
		REPLACEMENT_LIMIT = 1.0
		SIM_THRESH = 0.95
		fpr = FingerPrinter()
		fprsh = FingerPrinterSimHash()
		k_len = 40

		correct = 0.
		correctsh = 0.
		for x in range(iterations):

			rand_doc1 = self.document_set.get_random_document()
			rand_doc2 = self.document_set.get_random_document()

			ratio1 = random.random()*REPLACEMENT_LIMIT 
			ratio2 = random.random()*REPLACEMENT_LIMIT
			shorter = ratio1 if ratio1 < ratio2 else ratio2
			longer = ratio2 if ratio1 < ratio2 else ratio1

			body1 = self.overlap(rand_doc1[1],rand_doc2[1],shorter)
			body2 = self.overlap(rand_doc1[1],rand_doc2[1],longer)


			fpsh = fprsh.fingerprints(rand_doc1[1],k_len,win_len)
			fp = fpr.fingerprints(rand_doc1[1],k_len,win_len)

			fp1 = fpr.fingerprints(body1,k_len,win_len)
			fpsh1 = fprsh.fingerprints(body1,k_len,win_len)
			fp2 = fpr.fingerprints(body2,k_len,win_len)
			fpsh2 = fprsh.fingerprints(body2,k_len,win_len)

			if fpr.overlap_score(fp,fp1) < fpr.overlap_score(fp,fp2):
				correct += 1.

			if fprsh.overlap_score(fpsh,fpsh1, SIM_THRESH) < fprsh.overlap_score(fpsh,fpsh2, SIM_THRESH):
				correctsh += 1.

		return (correct/iterations, correctsh/iterations)

	#  let there be document A and document B. insert an excerpt from A into B resulting in C and C' where excerpt is longer in C'. Check if the overlap score is higher for C'
	def compare_fingerprinter(self,iterations, k_len = 40, win_ratio = None, win_len = 10):
		REPLACEMENT_LIMIT = 1.0
		fpr = FingerPrinter()

		correct = 0.
		for x in range(iterations):
			rand_doc1 = self.document_set.get_random_document()
			rand_doc2 = self.document_set.get_random_document()

			ratio1 = random.random()*REPLACEMENT_LIMIT 
			ratio2 = random.random()*REPLACEMENT_LIMIT
			shorter = ratio1 if ratio1 < ratio2 else ratio2
			longer = ratio2 if ratio1 < ratio2 else ratio1

			body1 = self.overlap(rand_doc1[1],rand_doc2[1],shorter)
			body2 = self.overlap(rand_doc1[1],rand_doc2[1],longer)


			if win_ratio != None:
				win_len = int(math.ceil(win_ratio*len(rand_doc1[1])))

			fp = fpr.fingerprints(rand_doc1[1],k_len,win_len)

			if win_ratio != None:
				win_len = int(math.ceil(win_ratio*len(body1)))

			fp1 = fpr.fingerprints(body1,k_len,win_len)
			fp2 = fpr.fingerprints(body2,k_len,win_len)

			if fpr.overlap_score(fp,fp1) < fpr.overlap_score(fp,fp2):
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



	def test_fingerprinter_doclength(self,iterations):
		REPLACEMENT_LIMIT = 1.0

		fpr = FingerPrinter()
		k_len = 20
		win_len = 40

		for i in range(iterations):
			rand_doc1 = self.document_set.get_random_document()
			rand_doc2 = self.document_set.get_random_document()
			fp = fpr.fingerprints(rand_doc1[1],k_len,win_len)

			correct = 0.
			for j in range(100):
				ratio1 = random.random()*REPLACEMENT_LIMIT 
				ratio2 = random.random()*REPLACEMENT_LIMIT
				shorter = ratio1 if ratio1 < ratio2 else ratio2
				longer = ratio2 if ratio1 < ratio2 else ratio1

				body1 = self.overlap(rand_doc1[1],rand_doc2[1],shorter)
				body2 = self.overlap(rand_doc1[1],rand_doc2[1],longer)

				
				fp1 = fpr.fingerprints(body1,k_len,win_len)
				fp2 = fpr.fingerprints(body2,k_len,win_len)

				if fpr.overlap_score(fp,fp1) < fpr.overlap_score(fp,fp2):
					correct += 1.
			
			score = correct / 100.
			print str(len(rand_doc2[1])) + "\t" + str(score)





	def benchmark_fingerprinter(self, iterations):

		k_len = 40
		win_len = 80
		fpr = FingerPrinter()

		t0 = time.clock()
		for x in range(iterations):
			rand_doc1 = self.document_set.get_random_document()
			rand_doc2 = self.document_set.get_random_document()
			fp1 = fpr.fingerprints(rand_doc1[1],k_len,win_len)
			fp2 = fpr.fingerprints(rand_doc2[1],k_len,win_len)
			overlap = fpr.overlap_score(fp1,fp2)
		t1 = time.clock()
		span = t1-t0
		return span


	def benchmark_fingerprintersimhash(self,iterations):
		k_len = 40
		win_len = 80
		fprsh = FingerPrinterSimHash()

		t0 = time.clock()
		for x in range(iterations):
			rand_doc1 = self.document_set.get_random_document()
			rand_doc2 = self.document_set.get_random_document()
			fp1 = fprsh.fingerprints(rand_doc1[1],k_len,win_len)
			fp2 = fprsh.fingerprints(rand_doc2[1],k_len,win_len)
			overlap = fprsh.overlap_score(fp1,fp2, 0.95)
		t1 = time.clock()
		span = t1-t0
		return span

	def benchmark_memory_fingerprinter(self,iterations):
		k_len = 40
		win_len = 80
		fpr = FingerPrinter()

		for x in range(iterations):
			rand_doc1 = self.document_set.get_random_document()
			rand_doc2 = self.document_set.get_random_document()
			fp1 = fpr.fingerprints(rand_doc1[1],k_len,win_len)
			fp2 = fpr.fingerprints(rand_doc2[1],k_len,win_len)
			overlap = fpr.overlap_score(fp1,fp2)
		return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000	

	def benchmark_memory_fingerprintersimhash(self,iterations):
		k_len = 40
		win_len = 80
		fprsh = FingerPrinterSimHash()

		for x in range(iterations):
			rand_doc1 = self.document_set.get_random_document()
			rand_doc2 = self.document_set.get_random_document()
			fp1 = fprsh.fingerprints(rand_doc1[1],k_len,win_len)
			fp2 = fprsh.fingerprints(rand_doc2[1],k_len,win_len)
			overlap = fprsh.overlap_score(fp1,fp2, 0.95)

		return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000	


	def benchmark_simhashkgram(self,iterations,hash_length, k):
		t0 = time.clock()
		simhashes = {}
		for i in range(iterations):
			title1 = self.select_random_document()
			title2 = self.select_random_document()
			if title1 not in simhashes:
				simhashes[title1] = SimHashKGram(self.documents[title1],hash_length,k)
			if title2 not in simhashes:
				simhashes[title2] = SimHashKGram(self.documents[title2],hash_length,k)
			sh1 = simhashes[title1]
			sh2 = simhashes[title2]
			sim = sh1.similarity(sh2)
		t1 = time.clock()
		span = t1-t0
		return span

	def benchmark_memory_simhash(self,iterations, hash_length, token_length):
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
		return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000	





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
		return span


	def benchmark_memory_tfidf(self,iterations):
		ds = DocSim(self.document_set)
		for i in range(iterations):
			title1 = self.select_random_document()
			title2 = self.select_random_document()
			sim = ds.similarity(title1,title2)

		return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000	



	def benchmark_tfidf(self,iterations):
		t0 = time.clock()
		ds = DocSim(self.document_set)
		for i in range(iterations):
			title1 = self.select_random_document()
			title2 = self.select_random_document()
			sim = ds.similarity(title1,title2)

		t1 = time.clock()
		span = t1 - t0
		return span






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


	# replace some section of document2 with an excerpt from document1
	def overlap(self, document1, document2, percentage_change):
		words1 = document1.split()
		words2 = document2.split()

		num_words = int(percentage_change*len(words2))
		if num_words > len(words1):
			num_words = len(words1)

		i = random.randint(0, len(words1) - num_words)
		excerpt = words1[i:i+num_words]

		j = random.randint(0,len(words2) - num_words)
		words2[j:j+num_words] = excerpt
		return " ".join(words2)




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


	i = int(sys.argv[2])
	print str(i) + "\t" + str(th.benchmark_memory_fingerprintersimhash(i))

	# # see how the fingerprinter accuracy changes as the document length increases
	# th.test_fingerprinter_doclength(1000)

	# # perfomance benchmarking for fingerprinter and fpsh

	# for i in range(1,1000):
	# 	num_iter = i*10
	# 	time_fp = th.benchmark_fingerprinter(num_iter)
	# 	time_fpsh = th.benchmark_fingerprintersimhash(num_iter)
	# 	print str(num_iter) + "\t" + str(time_fp) + "\t" + str(time_fpsh)



	#print th.benchmark_memory_tfidf(700)

	# print th.benchmark_memory_simhash(700,128,1)
		
	# for i in range(1,100):
	# 	num_iter = i*10
	# 	mem = th.benchmark_memory_simhash(num_iter,128,1)
	# 	print str(num_iter) + "\t" + str(mem)

	# Performance Benchmarking Code between simhash, simhashkgram,and tfidf
	# for i in range (1,100):
	# 	num_iter = i*10
	# 	time_sh = th.benchmark_simhash(num_iter,128,1)
	# 	time_shk = th.benchmark_simhashkgram(num_iter,128,5)
	# 	time_tfidf = th.benchmark_tfidf(num_iter)
	# 	print str(num_iter) + "\t" + str(time_sh) + "\t" + str(time_shk) + "\t" + str(time_tfidf)

	# # performance bench marking code between fingerprinter and fingerprintersimhash
	# for i in range(1,1000):
	# 	num_iter = i*10
	# 	time_fp = th.benchmark_fingerprinter(num_iter)
	# 	time_fpsh = th.benchmark_fingerprintersimhash(num_iter)

	# 	print str(num_iter) + "\t" + str(time_fp) + "\t" + str(time_fpsh)



	# # see how the accuracy of fingerprinter and fingerprintersimhash change as the window length changes
	# for w in range(1,1000):
	# 	win_len = w*20
	# 	score = th.temp(50,win_len)
	# 	print str(win_len) + "\t" + str(score[0]) + "\t" + str(score[1])



	# # test accuracy of fingerprinter by modifying a document twice and seeing which version has a higher fingerprint overlap 
	# print th.compare_fingerprinter(100, 20)


	# # test accuracy of fingerprinter as the window ratio changes
	# for i in range(1,10000):
	# 	try: 
	# 		print str(i) + "\t" + str(th.compare_fingerprinter(100,20,None,i))
	# 	except:
	# 		continue

	# # test the accuracy of fingerprinter as the k length changes
	# for k in range(1,4000):
	# 	score = None
	# 	while score is None:
	# 		try:
	# 			score = th.compare_fingerprinter(100,k,None,40)
	# 			print str(k) + "\t" + str(score)
	# 		except:
	# 			pass

	# # testing accurayc of simhashkgram by modifying a document twice and seeing which version is more similar
	# print th.compare_simhashkgram_replace(100,128,5)

	# # seeing how the accuracy of simhashkgram changes as k changes
	# for i in range(21,50):
	# 	print str(i) + "\t" + str(th.compare_simhashkgram_replace(100,128,i))


	# # testing the accuracy of simhash by modifying a document twice and seeing which version is more similar
	# print th.compare_simhash_replace(100, 128)
	
	# # Seeing how the accuracy of SimHash changes as the hash length changes
	# for i in range(129,513):
	# 	print str(i) + "\t" + str(th.compare_simhash_replace(100, i))


	#print th.compare_tfidf_replace(10000)


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






