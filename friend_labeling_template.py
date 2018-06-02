import os, json

def main():
	# chats_dir = './raw_chats'
	chats_dir = './Claire'
	label_dir = './labels'
	contacts = [(contact.replace('.csv', '')) for contact in os.listdir(chats_dir)]
	labels_dict = {}

	# for contact in contacts:
	# 	if contact in ['WeChat Team', '.DS_S', '.DS_Store', 'File Transfer']:
	# 		continue
	# 	else:
	# 		labels_dict[contact] = ''

	for contact in contacts:
		if contact in ['WeChat Team', '.DS_S', '.DS_Store', 'File Transfer']:
			continue
		else:
			public_account_flag = False
			with open(os.path.join(chats_dir, contact + '.csv'), errors='ignore', encoding='utf-8') as f_chat:
				words = []
				for i, line in enumerate(f_chat):
					if i > 0:
						## Identify public account
						record = line.split(',')
						if i == 1 and len(record) == 4 and record[2] == '':
							public_account_flag = True
							break
						else:
							labels_dict[contact] = ''
							break

	with open(os.path.join(label_dir, 'claire_labels.json'), 'w', encoding='utf-8') as fp:
		json.dump(labels_dict, fp, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()