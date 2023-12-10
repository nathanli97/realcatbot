import logging
import os
import random
import re
import string

from telegram import Update
from telegram.constants import ChatType
from telegram.ext import ApplicationBuilder, AIORateLimiter, ContextTypes, MessageHandler, filters

bot_token = os.environ['BOT_TOKEN']
bot_webhook_port = int(os.environ['WEBHOOK_PORT'])
bot_webhook = os.environ['WEBHOOK']


def random_id_generator(size=64, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


async def recv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg.chat.type is not ChatType.GROUP and \
            msg.chat.type is not ChatType.SUPERGROUP:
        return

    if msg.text.startswith("+"):
        if not msg.reply_to_message:
            logging.getLogger("Recv").warning("No reply to")
            return

        reply_to_user = update.message.reply_to_message.from_user

        text = msg.text[1:]
        match = re.fullmatch(r"(\d+)( .+)?", text)
        if match:
            num = int(match.group(1))
            what = match.group(2)

            unit = "只兔纸"
            if what:
                unit = what

            await update.message.reply_text(f'{msg.from_user.full_name} 给 {reply_to_user.full_name} 加了{num}{unit}!')
        else:
            logging.getLogger("Recv").warning("REGEX match failed")
    elif msg.text.startswith("!") or msg.text.startswith("！"):
        message = msg.text[1:]
        target_user_name = msg.from_user.full_name

        if update.message.reply_to_message:
            target_user_name = update.message.reply_to_message.from_user.full_name

            if message == "kiss":
                await update.message.reply_text(f'{msg.from_user.full_name} 亲了一口 {target_user_name}!')
                return
        if message == "ban":
            await update.message.reply_text(f'{target_user_name} 已封禁！')
            return
        elif message == "kick":
            await update.message.reply_text(f'{target_user_name} 已踢出！')
            return


def main():
    logging.basicConfig(
        format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
        level=logging.DEBUG
    )

    application = ApplicationBuilder().token(bot_token).read_timeout(5000).rate_limiter(
        AIORateLimiter()).build()

    msg_recv_handler = MessageHandler(callback=recv, filters=filters.ChatType.GROUPS & (~filters.COMMAND))
    application.add_handler(msg_recv_handler)

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
