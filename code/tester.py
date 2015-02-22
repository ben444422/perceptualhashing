from simhash import SimHash
import sys
import operator
import random
import string


class DocumentSet:
	def __init__(self):
		self.documents = self.load_documents()

	# load the documents from stdin
	def load_documents(self):
		data = {}
		for line in sys.stdin:
			if line.strip()[0] == "#":
				continue
			tokens = line.split("<")
			title = line.split()[0]
			title = title[1:-1]
			title_tokens = title.split("/")
			title = title_tokens[-1]
			tokens2 = tokens[2].split("> ")
			text = tokens2[1][1:-5]
			data[title] = text
		return data

	# returns a random document from the document set. Does not modify the 
	# document set
	def get_random_document(self):
		return random.sample(self.documents.items(), 1)[0]


class TestHouse:
	def __init__(self, docSet):
		self.document_set = docSet
		self.documents = docSet.documents


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




	def test_random_change(self, change_type, token_length, percentage_change, sim_threshold):

		for title in self.documents:
			text = self.documents[title]
			text_mod = ""
			if change_type == "replace":
				text_mod = self.replace(text,percentage_change)
			elif change_type == "permute":
				text_mod = self.permute(text, percentage_change)
			else:
				raise Exception("Invalid document change type")
			h1 = SimHash(text,128, token_length)
			h2 = SimHash(text_mod,128, token_length)
			sim = h1.similarity(h2)
			print title + " " + str(sim)


	def replace(self, document, percentage_change):
		words = document.split()
		num_changes = int(len(words)*percentage_change)
		indices = random.sample(range(len(words)), num_changes)
		for i in indices:
			newword = ""
			for c in words[i]:
				if random.randint(0,1) == 0:
					newword += random.choice(string.letters)
				else:
					newword += c 
			words[i] = newword
		newdoc = " ".join(words)	
		return newdoc

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

if __name__ == "__main__":
	ds = DocumentSet()

	th = TestHouse(ds)
#	th.test_document_similarity()
	th.test_random_change("permute", 2, 0.5,0.0001)

