import os, gensim
from gensim import corpora, models

def main():
	data_dir = './processed_chats'
	docs = []

	with open(os.path.join(data_dir, 'processed_chats.txt'), 'r') as f_chat:
		chats = f_chat.readlines()
		for chat in chats:
			words = chat.split('||||')[1].split(' ')
			doc = words[:-1] + [words[-1].replace('\n', '')]
			docs.append(doc)

	# Create the term dictionary of the courpus, where every unique term is assigned an index. 
	dictionary = corpora.Dictionary(docs)

	# Filter out tokens that appear in less than no_below documents (absolute number) or
	# more than no_above documents (fraction of total corpus size)
	dictionary.filter_extremes(no_below=5, no_above=0.5)
	print(dictionary)

	# Convert list of documents (corpus) into Document Term Matrix using dictionary prepared above.
	doc_term_matrix = [dictionary.doc2bow(doc) for doc in docs]

	# Initialize a model
	tfidf = models.TfidfModel(doc_term_matrix)

	# Use the model to transform vectors, apply a transformation to a whole corpus
	corpus_tfidf = tfidf[doc_term_matrix]

	# Extract 100 LDA topics, using 1 pass and updating once every 1 chunk (10,000 documents), using 500 iterations
	lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=3, iterations=500)

	# print topics composition, and their scores, for the first document. You will see that only few topics are represented; the others have a nil score.
	for index, score in sorted(lda[corpus_tfidf[0]], key=lambda tup: -1*tup[1]):
		print("Score: {}\t Topic: {}".format(score, lda.print_topic(index, 10)))

    # print the most contributing words for 3 randomly selected topics
	#lda.print_topics(3)

if __name__ == "__main__":
	main()