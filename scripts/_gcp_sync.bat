@echo off
gcloud compute ssh patrick.jang@trading-bot-seoul --project=tradingbot-korea --zone=us-east1-c --command="ls /home/patrick.jang/ && echo --- && find /home/patrick.jang -maxdepth 2 -name '.git' -exec git -C {}/.. remote -v \; 2>/dev/null"
