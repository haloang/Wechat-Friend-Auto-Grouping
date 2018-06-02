import os, json, itertools

def main():
	output_dir = './output/'
	chat_grps = json.load(open(output_dir + 'group_chat_friends.json'))
	friend_pair_list = []
	for key in chat_grps:
		grp_members = chat_grps[key]
		friend_pairs = list(itertools.combinations(grp_members, 2))
		friend_pair_list += friend_pairs
	
	friend_pair_sets = set(friend_pair_list)

	fout = open(os.path.join(output_dir, 'friend_pairs.csv'), 'w', encoding='utf-8')
	for friend_pair_set in friend_pair_sets:
		friends = list(friend_pair_set)
		row = ','.join(friends) + ',' + str(friend_pair_list.count(friend_pair_set))
		fout.write('%s\n' %row)
	fout.close()

if __name__ == '__main__':
    main()