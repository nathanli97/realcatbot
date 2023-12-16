import logging
import re

from telegram import Update
from telegram.ext import ContextTypes
from utils import get_message_username


def check_contain_chinese(check_str):
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def check_contain_engidlist(check_str):
    contain_en = bool(re.search('[a-z]', check_str)) or bool(re.search('[0-9]', check_str))
    return contain_en


def check_contain_valid_str(check_str):
    """判断字符串是否包含有效字符：中文 or 英文 or 数字"""
    valid_res = check_contain_chinese(check_str) or check_contain_engidlist(check_str)
    return valid_res


async def fake_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    message = msg.text[1:]

    if not msg.reply_to_message:
        logging.getLogger("Recv").warning("No reply to")
        return

    from_user_name = get_message_username(msg)
    target_user_name = get_message_username(msg.reply_to_message)

    if check_contain_valid_str(message):
        if message == "kiss":
            await update.message.reply_text(f'{from_user_name} 亲了一口 {target_user_name}!')
            return
        if message == "mua":
            await update.message.reply_text(f'{from_user_name} 冲过去抱住 {target_user_name}，一顿狂亲!')
            return
        elif message == "bite":
            await update.message.reply_text(f'{from_user_name} 咬了一口 {target_user_name}!')
            return
        elif message == "stick":
            await update.message.reply_text(f'{from_user_name} 贴贴了 {target_user_name}!')
            return
        elif message == "ban":
            await update.message.reply_text(f'{target_user_name} 已封禁！')
            return
        elif message == "unban":
            await update.message.reply_text(f'{target_user_name} 已解禁！')
            return
        elif message == "kick":
            await update.message.reply_text(f'{target_user_name} 已踢出！')
        else:
            action = message
            what = ''
            match = re.fullmatch(r"(.+) (.+)", message)
            if match:
                action = match.group(1)
                what = match.group(2)
                await update.message.reply_text(f'{from_user_name} {action} {target_user_name} {what}!')
            else:
                await update.message.reply_text(f'{from_user_name} {action} {target_user_name}!')
