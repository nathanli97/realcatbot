from telegram import Message


def get_message_username(msg: Message) -> str:
    user_name = msg.from_user.full_name
    if msg.sender_chat and msg.sender_chat.title:
        user_name = msg.sender_chat.title

    if msg.from_user.username and msg.from_user.username == 'GroupAnonymousBot':
        user_name = msg.chat.title

        if msg.author_signature:
            user_name += f' ({msg.author_signature})'
    return user_name