import time

message_count_warning_users = []  # 下个版本再实现持久化保存
scores = {}
lastjoke = {}
MaxScores = 100
scores_randomslist = ['喵~', '捏~', '哼!', '**的', 'baka!']

last_known_day = -1


def msgcount(chatid: int, msg_user: str):
    global last_known_day
    gmt = time.gmtime()
    day = gmt.tm_yday

    if last_known_day != -1 and day != last_known_day:
        scores.clear()
    else:
        last_known_day = day

    chatid_str = str(chatid)
    if chatid_str not in scores:
        scores[chatid_str] = {}
    if msg_user not in scores[chatid_str]:
        scores[chatid_str][msg_user] = 0
    scores[chatid_str][msg_user] = scores[chatid_str][msg_user] + 1
    if scores[chatid_str][msg_user] > MaxScores and msg_user in message_count_warning_users:
        return True, f'{msg_user} 今天水太多啦！去做点其他事情吧。'
    else:
        return False, ''
