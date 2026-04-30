#!/usr/bin/env python3
import re

src = "/home/patrick.jang/Macro-Pulse/.env"
dst = "/home/patrick.jang/trading-bot-seoul/.env"

# Read new values from Macro-Pulse .env
new_vals = {}
with open(src) as f:
    for line in f:
        for key in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
            if line.startswith(key + "="):
                new_vals[key] = line.strip()

# Update trading-bot-seoul .env
with open(dst) as f:
    lines = f.readlines()

updated = []
for line in lines:
    replaced = False
    for key, new_line in new_vals.items():
        if line.startswith(key + "="):
            updated.append(new_line + "\n")
            replaced = True
            break
    if not replaced:
        updated.append(line)

with open(dst, "w") as f:
    f.writelines(updated)

print("Updated:", list(new_vals.keys()))
print("Verify (masked):")
with open(dst) as f:
    for line in f:
        if line.startswith("TELEGRAM_BOT_TOKEN=") or line.startswith("TELEGRAM_CHAT_ID="):
            key = line.split("=")[0]
            print(f"  {key}=***")
