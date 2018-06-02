import os, json
import numpy as np
import chat_lda_topic_modeler as topic_modeler
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold
from sklearn.metrics import classification_report, precision_score, recall_score, f1_score, accuracy_score


def main():
	contacts, topic_dist_matrix = topic_modeler.main()
	print('There are ' + str(len(contacts)) + ' contacts in total.')

	# print(topic_dist_matrix.shape)
	feature_dir = './output/'
	labels_dir = './labels/'
	features = json.load(open(feature_dir + 'claire_features.json'))
	# labels = json.load(open(labels_dir + 'labels.json'))
	labels = json.load(open(labels_dir + 'claire_labels.json'))
	grp_contacts = json.load(open(feature_dir + 'group_chat_friends.json'))

	## Incorporate topic distribution probability of group chats into individual chats
	for key in grp_contacts:
		grp_friends = grp_contacts[key]
		if key not in contacts:
			continue
		else:
			grp_id = contacts.index(key)
			for grp_friend in grp_friends:
				if grp_friend in contacts:
					friend_id = contacts.index(grp_friend)
					topic_dist_matrix[friend_id, ] = np.sum([topic_dist_matrix[friend_id, ], topic_dist_matrix[grp_id, ]], axis=0)

	## Normalize the topic distribution probabilities
	topic_dist_matrix = [(row / np.sum(row)) for row in topic_dist_matrix]

	## Remove group contacts from the contact list as well their corresponding topic distribution
	grp_contacts_indices = []
	for contact in contacts:
		if contact in grp_contacts:
			grp_contacts_indices.append(contacts.index(contact))
	new_contacts = [contact for contact in contacts if contact not in grp_contacts]
	topic_dist_list = list(topic_dist_matrix)
	topic_dist_list = [i for j, i in enumerate(topic_dist_list) if j not in grp_contacts_indices]
	topic_dist_matrix = np.array(topic_dist_list)
	print(topic_dist_matrix.shape)

	features_matrix = []
	y = []
	N = len(new_contacts)
	print('There are ' + str(N) + ' contacts left after removing the group contacts.')
	for i in range(N):
		contact = new_contacts[i]
		no_of_msgs = int(features[contact]['no_of_msgs'])
		avg_len_of_msg = float(features[contact]['avg_len_of_msg'])
		punc_usage = float(features[contact]['punc_usage'])
		senti_score = float(features[contact]['senti_score'])
		emoji_usage = float(features[contact]['emoji_usage'])
		noun_usage = float(features[contact]['noun_usage'])
		verb_usage = float(features[contact]['verb_usage'])
		adj_usage = float(features[contact]['adj_usage'])
		ely_usage = float(features[contact]['ely_usage'])
		stopwords_usage = float(features[contact]['stopwords_usage'])
		no_of_common_grps = float(features[contact]['no_of_common_grps'])
		feature_row = [no_of_msgs, avg_len_of_msg, punc_usage, senti_score, emoji_usage, 
					   noun_usage, verb_usage, adj_usage, ely_usage, stopwords_usage, no_of_common_grps]
		features_matrix.append(feature_row)
		y.append(labels[contact])

	features_matrix = np.array(features_matrix)
	full_matrix = np.concatenate((topic_dist_matrix, features_matrix), axis=1)
	# full_matrix  = features_matrix
	y = np.array(y)

	print("Start training and predict...")
	kf = KFold(n_splits=10)
	avg_p = 0
	avg_r = 0
	avg_f1 = 0
	avg_accu = 0

	for train, test in kf.split(full_matrix):
		# model = MultinomialNB().fit(full_matrix[train], y[train])
		model = RandomForestClassifier(n_estimators = 1000, max_features = 16, random_state=0).fit(full_matrix[train], y[train])
		predicts = model.predict(full_matrix[test])
		print(classification_report(y[test], predicts))
		avg_p += precision_score(y[test], predicts, average='macro')
		avg_r += recall_score(y[test], predicts, average='macro')
		avg_f1 += f1_score(y[test], predicts, average='macro')
		avg_accu += accuracy_score(y[test],predicts)

	print('Average Precision is %f.' %(avg_p/10.0))
	print('Average Recall is %f.' %(avg_r/10.0))
	print('Average F1 score is %f.' %(avg_f1/10.0))
	print('Average Accuracy is %f.' %(avg_accu/10.0))

if __name__ == '__main__':
    main()