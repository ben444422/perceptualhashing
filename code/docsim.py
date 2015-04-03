from util import DocumentSet
from gensim import corpora, models, similarities
from nltk.corpus import stopwords

class DocSim:
	def __init__(self, doc_set):
		self.documents = doc_set.documents
		self.process()

	def process(self):
		documents = [title + " " + body for title,body in self.documents.items()]
		self.doc_list = [title for title,body in self.documents.items()]	
		self.inverted_doc_index = {}
		for index,title in enumerate(self.doc_list):
			self.inverted_doc_index[title] = index
		texts = [[word for word in document.lower().split() if word not in stopwords.words('english')] for document in documents]
		self.dictionary = corpora.Dictionary(texts)
		self.corpus = [self.dictionary.doc2bow(text) for text in texts]
		self.tfidf = models.TfidfModel(self.corpus)
		self.index = similarities.SparseMatrixSimilarity(self.tfidf[self.corpus], num_features=len(self.dictionary))



	def similarity(self,title1,title2):
		if title1 not in self.inverted_doc_index or title2 not in self.inverted_doc_index:
			raise ValueError("Title does not exist in the documents")
		index1 = self.inverted_doc_index[title1]
		index2 = self.inverted_doc_index[title2]
		return self.index[self.tfidf[self.corpus[index1]]][index2]

	def similarity_new_doc(self,title1,new_doc):
		new_vec = self.dictionary.doc2bow([word for word in new_doc.lower().split() if word not in stopwords.words('english')])
		return self.index[self.tfidf[new_vec]][self.inverted_doc_index[title1]]



		



