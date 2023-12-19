import logging
import os
import random
import re
import string
import time
import cn2an

from telegram import Update
from telegram.constants import ChatType
from telegram.ext import ApplicationBuilder, AIORateLimiter, ContextTypes, MessageHandler, filters, CommandHandler

from collections import defaultdict

from fake_commands import fake_command
from message_count import message_count_warning_users, scores, scores_randomslist, msgcount
from plusminus import plus_or_minus
from utils import get_message_username

try:
    bot_token = os.environ['BOT_TOKEN']
    bot_webhook_port = int(os.environ['WEBHOOK_PORT'])
    bot_webhook = os.environ['WEBHOOK']
except KeyError:
    print("The following environment variables are required: BOT_TOKEN, WEBHOOK_PORT, WEBHOOK")
    print("If using debug mode(No WEBHOOK Configured), ")
    print(
        "please feel free to set WEBHOOK_PORT and WEBHOOK environment variables to any value, the program will not to")
    print("use the WEBHOOK_PORT and WEBHOOK environment variables.")
    exit(-1)
try:
    bot_debug = os.environ['BOT_DEBUG'].upper() == "TRUE"
except KeyError:
    bot_debug = False


def random_id_generator(size=64, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


async def enable_message_count_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    msguserid = str(msg.from_user.id)
    message_count_warning_users.append(msguserid)
    await update.message.reply_text(f'{msg.from_user.full_name} Enabled Water Detector')


async def disable_message_count_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    msguserid = str(msg.from_user.id)
    message_count_warning_users.remove(msguserid)
    await update.message.reply_text(f'{msg.from_user.full_name} Disabled Water Detector')


async def scores_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.chat.id) not in scores:
        header = ["今日还没有水王上榜~"]
    else:
        header = ["本群今日水王排行榜(每天8点重置一次)"]
        top_players = sorted(scores[str(update.message.chat.id)].items(), key=lambda e: e[1], reverse=True)[:14]
        count = 0
        for idx, (key, value) in enumerate(top_players, start=1):
            if value > 20:
                position = cn2an.an2cn(idx, "up")
                header.append(f'第 {position} 名 {key} 水了 {value} 条信息')
                count += 1
        if len(top_players) < len(scores[str(update.message.chat.id)]):
            header.append(f'还有几个水逼我就不列举了，{random.choice(scores_randomslist)}')
        if count == 0:
            header = ["今日还没有水王上榜~"]
    await update.message.reply_text('\n'.join(header))


async def recv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    msg_user = get_message_username(msg)

    if msg.chat.type is not ChatType.GROUP and \
            msg.chat.type is not ChatType.SUPERGROUP:
        return
    msstatus, msmessage = msgcount(update.message.chat.id, msg_user)
    if msstatus:
        await update.message.reply_text(msmessage)
        return
    if not msg.text:
        # 这条消息不包含任何文本信息
        return
    if msg.text.startswith("+") or msg.text.startswith("-"):
        await plus_or_minus(update, context)
    elif msg.text.startswith("!") or msg.text.startswith("！"):
        await fake_command(update, context)
        # else:
        #     random_message = random.choice(random_message_list)
        #     if msg_user not in lastjoke:
        #         lastjoke[msg_user] = random_message
        #     else:
        #         while lastjoke[msg_user] == random_message:
        #             random_message = random.choice(random_message_list)
        #     await update.message.reply_text(f'{msg_user}{random_message}')


def main():
    if not bot_debug:
        logging.basicConfig(
            format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
            level=logging.INFO
        )
    else:
        logging.basicConfig(
            format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
            level=logging.DEBUG,
            filename='tgbot.log'
        )

    application = ApplicationBuilder().token(bot_token).read_timeout(5000).rate_limiter(
        AIORateLimiter()).build()

    msg_recv_handler = MessageHandler(callback=recv, filters=filters.ChatType.GROUPS & (~filters.COMMAND))
    enable_message_count_warning_handler = CommandHandler('enable_message_count_warning',
                                                          callback=enable_message_count_warning)
    disable_message_count_warning_handler = CommandHandler('disable_message_count_warning',
                                                           callback=disable_message_count_warning)
    scores_list_handler = CommandHandler('scores_list', callback=scores_list)
    application.add_handler(msg_recv_handler)
    application.add_handler(enable_message_count_warning_handler)
    application.add_handler(disable_message_count_warning_handler)
    application.add_handler(scores_list_handler)

    bot_secret_id = random_id_generator(32)
    logging.getLogger('Bot').warning(f'Bot running with random ID "{bot_secret_id}"')

    if not bot_debug:
        application.run_webhook(
            listen='127.0.0.1',
            port=bot_webhook_port,
            secret_token=bot_secret_id,
            webhook_url=bot_webhook
        )
    else:
        application.run_polling()


if __name__ == '__main__':
    main()
