import os, json

def main():
    # grp_chats_dir = './group_chat_friend_lists'
    grp_chats_dir = './Claire_groups'
    output_dir = './output'
    # chats_dir = './raw_chats'
    chats_dir = './Claire'
    MEMBER_IDENTIFIER = 'ng-repeat="item in currentContact.MemberList"'
    contacts = [(contact.replace('.csv', '')) for contact in os.listdir(chats_dir)]
    grp_chats = [(grp.replace('.txt', '')) for grp in os.listdir(grp_chats_dir)]
    grp_chats_dict = {}

    for grp_chat in grp_chats:
        with open(os.path.join(grp_chats_dir, grp_chat + '.txt'), 'r', encoding='utf-8') as f:
            htmls = f.readlines()

        friend_list = []
        for html in htmls:
            if MEMBER_IDENTIFIER in html:
                member_container = html.strip()[html.find('title')-1:]
                if '<img' in member_container:
                    member_name = member_container[:(member_container.find('<img'))]
                else:
                    member_name = member_container[:-2]
                if member_name in contacts:
                    friend_list.append(member_name)
        grp_chats_dict[grp_chat] = friend_list

    ## Export features to json file
    with open(os.path.join(output_dir, 'group_chat_friends.json'), 'w', encoding='utf-8') as fp:
        json.dump(grp_chats_dict, fp, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()