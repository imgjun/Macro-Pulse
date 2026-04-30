@echo off
gcloud compute ssh patrick.jang@trading-bot-seoul --project=tradingbot-korea --zone=us-east1-c --command="git -C /home/patrick.jang/Macro-Pulse show 9bfd310 -- .gitignore"
