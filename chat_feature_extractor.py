from zhon.hanzi import punctuation
from snownlp import SnowNLP
import os, re, string, json
import jieba.posseg
import numpy as np
import batch_chats_preprocessor_v2 as preprocessor

print("Extracting chat features...")
def main():
	# chats_dir = './raw_chats'
	chats_dir = './Claire'
	output_dir = './output/'
	dicts_dir = './dicts/'
	GROUP_CHAT_IDENTIFIER = "@chatroom"
	puncs = punctuation + string.punctuation	# Combine both Chinese and English punctuations
	contacts = [(contact.replace('.csv', '')) for contact in os.listdir(chats_dir)]
	grp_chats = json.load(open(output_dir + 'group_chat_friends.json'))
	feature_list = {}

	with open(os.path.join(dicts_dir, 'stopwords_v3.txt'), 'r', encoding='utf-8') as f_stop:
		stops = f_stop.readlines()
		stops = [(stop.replace('\n', '')) for stop in stops]

	for contact in contacts:
		if contact in ['WeChat Team', '.DS_S', '.DS_Store', 'File Transfer']:
			continue
		else:
			print(contact)
			public_account_flag = False
			with open(os.path.join(chats_dir, contact + '.csv'), errors='ignore', encoding='utf-8') as f_chat:
				msg_len_list = []
				sentiments = []
				use_of_puncs = 0
				use_of_emojis = 0
				use_of_nouns = 0
				use_of_verbs = 0
				use_of_adjs = 0
				use_of_ely = 0
				use_of_stopwords = 0
				for i, line in enumerate(f_chat):
					if i > 0:
						## Identify public account
						record = line.split(',')
						if i == 1 and len(record) == 4 and record[2] == '':
							public_account_flag = True
							break
						else:
							s = line.strip().replace('\n', '')
							if preprocessor.filter_msg(s):
								## Carefully extract the chat message
								position = s.find(contact)
								msg = s[(position+len(contact)+1):(len(s)-20)]

								## Identify group chat
								if GROUP_CHAT_IDENTIFIER in s and ':' in msg:
									msg = msg.split(':')[1]
								## Extract linguistic features before preprocessing
								segs = jieba.posseg.cut(msg)
								for seg in segs:
									if seg.flag == 'n':
										use_of_nouns += 1
									if seg.flag == 'v':
										use_of_verbs += 1
									if seg.flag == 'a':
										use_of_adjs += 1
									if seg.flag in ['e', 'l', 'y']:
										use_of_ely += 1
									if seg.word in stops:
										use_of_stopwords += 1
								msg = preprocessor.pre_process(msg)
								msg_len_list.append(len(msg))
								try:
									senti_score = SnowNLP(msg).sentiments
								except:
									senti_score = 0.5
								sentiments.append(senti_score)
								punc_list = re.findall('[{}]'.format(puncs), msg)
								use_of_puncs += len(punc_list)
								emoji_flag = msg.count('[')
								if emoji_flag > 0:
									use_of_emojis += min(emoji_flag, msg.count(']'))

				if len(msg_len_list) > 0:
					features = {}
					common_grps = []
					common_grp_counter = 0
					features['no_of_msgs'] = len(msg_len_list)
					features['avg_len_of_msg'] = round(np.mean(np.array(msg_len_list)), 4)
					features['punc_usage'] = round(use_of_puncs / features['no_of_msgs'], 4)
					polar_sentis = [sentiment for sentiment in sentiments if sentiment > 0.75 or sentiment < 0.25]
					features['senti_score'] = round(len(polar_sentis) / len(sentiments))
					# features['senti_score'] = round(np.mean(np.array(sentiments)), 4)
					features['emoji_usage'] = round(use_of_emojis / features['no_of_msgs'], 4)
					features['noun_usage'] = round(use_of_nouns / features['no_of_msgs'], 4)
					features['verb_usage'] = round(use_of_verbs / features['no_of_msgs'], 4)
					features['adj_usage'] = round(use_of_adjs / features['no_of_msgs'], 4)
					features['ely_usage'] = round(use_of_ely / features['no_of_msgs'], 4)
					features['stopwords_usage'] = round(use_of_stopwords / features['no_of_msgs'], 4)
					for key in grp_chats:
						if contact in grp_chats[key]:
							common_grps.append(key)
							common_grp_counter += 1
					features['no_of_common_grps'] = common_grp_counter
					features['common_grps'] = common_grps
					feature_list[contact] = features

	## Export features to json file
	with open(os.path.join(output_dir, 'claire_features.json'), 'w', encoding='utf-8') as fp:
		json.dump(feature_list, fp, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()