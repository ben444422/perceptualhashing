import sys
import random
import json


class DocumentSet:
	def __init__(self):
		self.documents = self.load_documents2()


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

	def load_documents2(self):
		data = {}
		file_name = sys.argv[1]
		js = open(file_name).read()
		for e in json.loads(js):
			data[e["title"]] = e["body"]
		return data	
	
	# returns a random document from the document set. Does not modify the 
	# document set
	def get_random_document(self):
		return random.sample(self.documents.items(), 1)[0]

