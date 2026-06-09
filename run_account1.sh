#!/bin/bash
# アカウント1（koshigaya_diet_seitai）ゴールデンタイム自動投稿ランナー
cd "$(dirname "$0")" || exit 1
set -a
. ./.env
set +a
/usr/bin/python3 auto_post.py >> cron.log 2>&1
