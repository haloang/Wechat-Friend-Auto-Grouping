import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import lda
import matplotlib.pyplot as plt
import seaborn as sns
import os

def get_lda_input(chats):
    corpus = [" ".join(word_list) for word_list in chats]
    vectorizer = CountVectorizer()
    # vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    # print(X.toarray(),vectorizer)
    return X.toarray(), vectorizer

def lda_train(weight, vectorizer, contacts):
    model = lda.LDA(n_topics=5, n_iter=1000, random_state=1)
    model.fit(weight)

    doc_num = len(weight)
    topic_word = model.topic_word_
    vocab = vectorizer.get_feature_names()

    n_top_words = 15
    for i, topic_dist in enumerate(topic_word):
        topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words + 1):-1]
        print('Topic {}: {}'.format(i, ' '.join(topic_words)))

    doc_topic = model.doc_topic_
    print(doc_topic, type(doc_topic))
    for i in range(doc_num):
        print("{} (top topic: {})".format(contacts[i], np.argsort(doc_topic[i])[:-4:-1]))

    plot_topic(doc_topic)
    return doc_topic
    

def plot_topic(doc_topic):
    f, ax = plt.subplots(figsize=(10, 4))
    cmap = sns.cubehelix_palette(start=1, rot=3, gamma=0.8, as_cmap=True)
    sns.heatmap(doc_topic, cmap=cmap, linewidths=0.05, ax=ax)
    ax.set_title('proportion per topic in every chat log')
    ax.set_xlabel('topic')
    ax.set_ylabel('contact')
    plt.show()

    # f.savefig('output/topic_heatmap.jpg', bbox_inches='tight')

def load_chats():
    output_dir = './processed_chats'
    chat_list = []
    contact_list = []

    with open(os.path.join(output_dir, 'processed_chats_claire.txt'), 'r', encoding='utf-8') as f_chats:
        chats = f_chats.readlines()

    for chat in chats:
        contact = chat.split('||||')[0]
        words = chat.split('||||')[1].split(',')
        doc = words[:-1] + [words[-1].replace('\n', '')]
        contact_list.append(contact)
        chat_list.append(doc)

    return [contact_list, chat_list]

def main():
    contacts, chats = load_chats()
    weight, vectorizer = get_lda_input(chats)
    topic_dist_matrix = lda_train(weight, vectorizer, contacts)
    # print(topic_dist_matrix)
    return [contacts, topic_dist_matrix]


if __name__ == '__main__':
    main()
