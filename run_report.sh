#!/bin/bash
# 前日分の日次レポートを生成（00:30実行想定）
cd "$(dirname "$0")" || exit 1
set -a
. ./.env
set +a
YDAY=$(/bin/date -v-1d "+%Y-%m-%d")
/usr/bin/python3 analyze_day.py "$YDAY" >> report.log 2>&1
