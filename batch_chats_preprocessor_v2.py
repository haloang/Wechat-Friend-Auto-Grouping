import re, os, jieba.posseg

def filter_msg(str):
	VALID_LENGTH = 10
	EMOJI_URL_IDENTIFIER = "emoji:http"
	EMOJI_NOURL_IDENTIFIER = "this an emoji"
	MSG_RECALL_IDENTIFIER = "recalled a message"
	MSG_RECALL_IDENTIFIER_CN = "你撤回了一条消息重新编辑"
	IMAGE_IDENTIFIER = "<msg>"
	ADD_NEW_FRIEND_IDENTIFIER = "as your WeChat contact. Start chatting!"
	BE_ADDED_AS_FRIEND_IDENTIFIER = "just added you to his/her contacts list"
	ACCEPT_FRIEND_REQUEST_IDENTIFIER = "I've accepted your friend request"
	INVITE_TO_GROUP_CHAT_IDENTIFIER = "sysmsgtemplate"
	ENABLE_FRIEND_VERIFICATION_IDENTIFIER = "to prevent harassment from strangers"

	if len(str) < 10:
		return False
	elif EMOJI_URL_IDENTIFIER in str:
		return False
	elif EMOJI_NOURL_IDENTIFIER in str:
		return False
	elif MSG_RECALL_IDENTIFIER in str:
		return False
	elif IMAGE_IDENTIFIER in str:
		return False
	elif ADD_NEW_FRIEND_IDENTIFIER in str:
		return False
	elif BE_ADDED_AS_FRIEND_IDENTIFIER in str:
		return False
	elif ACCEPT_FRIEND_REQUEST_IDENTIFIER in str:
		return False
	elif INVITE_TO_GROUP_CHAT_IDENTIFIER in str:
		return False
	elif ENABLE_FRIEND_VERIFICATION_IDENTIFIER in str:
		return False
	elif MSG_RECALL_IDENTIFIER_CN in str:
		return False
	else:
		return True


def rm_html_tags(str):
    html_prog = re.compile(r'<[^>]+>',re.S)
    return html_prog.sub('', str)

def rm_html_escape_characters(str):
    pattern_str = r'&quot;|&amp;|&lt;|&gt;|&nbsp;|&#34;|&#38;|&#60;|&#62;|&#160;|&#20284;|&#30524;|&#26684|&#43;|&#20540|&#23612;'
    escape_characters_prog = re.compile(pattern_str, re.S)
    return escape_characters_prog.sub('', str)

def rm_at_user(str):
    return re.sub(r'@[a-zA-Z_0-9]*', '', str)

def rm_url(str):
    return re.sub(r'http[s]?:[/+]?[a-zA-Z0-9_\.\/]*', '', str)

def rm_repeat_chars(str):
    return re.sub(r'(.)(\1){2,}', r'\1\1', str)

def rm_hashtag_symbol(str):
    return re.sub(r'#', '', str)

def rm_time(str):
    return re.sub(r'[0-9][0-9]:[0-9][0-9]', '', str)

def rm_digits(str):
	return re.sub(r'\d+', '', str)

def pre_process(str):
    # do not change the preprocessing order only if you know what you're doing 
    str = rm_url(str)        
    str = rm_at_user(str)        
    str = rm_repeat_chars(str) 
    str = rm_hashtag_symbol(str)       
    str = rm_time(str)
    str = rm_digits(str)

    return str

def cut_words_with_pos(text, stopwords):
    seg = jieba.posseg.cut(text)
    res = []
    for i in seg:
        if i.flag in ["a", "v", "x", "n", "an", "vn", "nz", "nt", "nr"] and is_fine_word(i.word, stopwords):
            res.append(i.word)
    return list(res)

# 过滤词长，过滤停用词，只保留中文
def is_fine_word(word, stopwords):
	min_length = 2
	rule = re.compile(r"^[\u4e00-\u9fa5]+$")
	if len(word) >= min_length and word not in stopwords and re.search(rule, word):
		return True
	else:
		return False


def main():
	# chats_dir = './raw_chats'
	chats_dir = './Claire'
	dicts_dir = './dicts'
	output_dir = './processed_chats'
	GROUP_CHAT_IDENTIFIER = "@chatroom"
	valid_contacts = []

	with open(os.path.join(dicts_dir, 'stopwords_v3.txt'), 'r', encoding='utf-8') as f_stop:
		stops = f_stop.readlines()
		stops = [(stop.replace('\n', '')) for stop in stops]

	contacts = [(contact.replace('.csv', '')) for contact in os.listdir(chats_dir)]
	for contact in contacts:
		stops += contact.split(' ')
	# print(stops)

	postprocess_msgs = []
	grp_chat_list = []
	for contact in contacts:
		if contact in ['WeChat Team', '.DS_S', '.DS_Store', 'File Transfer']:
			continue
		else:
			public_account_flag = False
			with open(os.path.join(chats_dir, contact + '.csv'), errors='ignore') as f_chat:
				words = []
				for i, line in enumerate(f_chat):
					if i > 0:
						## Identify public account
						record = line.split(',')
						if i == 1 and len(record) == 4 and record[2] == '':
							public_account_flag = True
							break
						else:
							s = line.strip().replace('\n', '')
							## Identify group chat
							if GROUP_CHAT_IDENTIFIER in s and i == 1:
								grp_chat_list.append(contact)
							if filter_msg(s):
								## Carefully extract the chat message
								position = s.find(contact)
								msg = s[(position+len(contact)+1):(len(s)-20)]								
								if ':' in msg:
									msg = msg.split(':')[1]										
								msg = pre_process(msg)
								words += cut_words_with_pos(msg, stops)
								
				words = list(filter(lambda word: word != '', words))
				if len(words) > 10:
					postprocess_msgs.append(words)
					valid_contacts.append(contact)
	
	no_of_contacts = len(valid_contacts)
	print(len(postprocess_msgs))
	if no_of_contacts == len(postprocess_msgs):
		fout = open(os.path.join(output_dir, 'processed_chats_claire.txt'), 'w', encoding='utf-8')
		for i in range(no_of_contacts):
			content = valid_contacts[i] + '||||' + (','.join(postprocess_msgs[i]))
			fout.write('%s\n' %content)

	grp_chats_set = set(grp_chat_list)
	grp_chats = list(grp_chats_set)
	f_grp = open(os.path.join(output_dir, 'grp_chats.txt'), 'w', encoding='utf-8')
	for grp_chat in grp_chats:
		f_grp.write('%s\n' %grp_chat)

if __name__ == "__main__":
	main()