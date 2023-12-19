from telegram import Message

from tgbot import MaxScores


def get_message_username(msg: Message) -> str:
    user_name = msg.from_user.full_name
    if msg.sender_chat and msg.sender_chat.title:
        user_name = msg.sender_chat.title

    if msg.from_user.username and msg.from_user.username == 'GroupAnonymousBot':
        user_name = msg.chat.title

        if msg.author_signature:
            user_name += f' ({msg.author_signature})'
    return user_name


def msgcount(scores, msg_user, message_count_warning_users):
    scores[msg_user] = scores[msg_user] + 1
    if scores[msg_user] > MaxScores and msg_user in message_count_warning_users:
        return True, f'{msg_user} 今天水太多啦！去做点其他事情吧。'
    else:
        return False, ''
