#!/bin/bash

cd /root/tgbot

source .env
python -m pip install -r requirements.txt
python3 tgbot.py &

while [ 1 ]
do
  if [ -z "`git pull | grep "Already up to date"`" ];then
    systemctl restart tgbot
    exit
  fi
  sleep 360
done
