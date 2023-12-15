import logging
import os
import random
import re
import string
import time
import schedule
import threading

from telegram import Update
from telegram.constants import ChatType
from telegram.ext import ApplicationBuilder, AIORateLimiter, ContextTypes, MessageHandler, filters, CommandHandler

from fake_commands import fake_command
from plusminus import plus_or_minus

bot_token = os.environ['BOT_TOKEN']
bot_webhook_port = int(os.environ['WEBHOOK_PORT'])
bot_webhook = os.environ['WEBHOOK']

message_count_warning_users = []  # 下个版本再实现持久化保存

scores = {}
lastjoke = {}
idtoname = {}
MaxScores = 150

score_lock = threading.Lock()


def cleanscores():
    scores.clear()


schedule.every(45).minutes.do(cleanscores)


def clear_score():
    schedule.run_pending()
    time.sleep(60)


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
    strkey = "本小时内水王排行榜"
    cnt = 0
    after = dict(sorted(scores.items(), key=lambda e: e[1], reverse=True))
    for key, value in after.items():
        cnt += 1
        if cnt > 11:
            strkey = strkey + "\n还有几个水逼我就不列举了，哼!"
            break
        strkey = strkey + "\n第{}名 {} 水了 {} 条信息".format(str(cnt), idtoname[key], value)
    await update.message.reply_text(strkey)


async def recv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    msguserid = str(msg.from_user.id)
    if msg.chat.type is not ChatType.GROUP and \
            msg.chat.type is not ChatType.SUPERGROUP:
        return
    if msguserid not in scores:
        scores[msguserid] = 0
        idtoname[msguserid] = msg.from_user.full_name
    else:
        scores[msguserid] = scores[msguserid] + 1
    if scores[msguserid] > MaxScores and msguserid in message_count_warning_users:
        await update.message.reply_text(f'{msg.from_user.full_name} 这个小时内水太多啦！去做点其他事情吧。')
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
        #     if msguserid not in lastjoke:
        #         lastjoke[msguserid] = random_message
        #     else:
        #         while lastjoke[msguserid] == random_message:
        #             random_message = random.choice(random_message_list)
        #     await update.message.reply_text(f'{msg.from_user.full_name}{random_message}')


def main():
    clear_score_thread = threading.Thread(target=clear_score)
    clear_score_thread.daemon = True  # 设置为守护线程，以确保程序退出时线程也会退出
    clear_score_thread.start()
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
    application.run_webhook(
        listen='127.0.0.1',
        port=bot_webhook_port,
        secret_token=bot_secret_id,
        webhook_url=bot_webhook
    )


if __name__ == '__main__':
    main()
