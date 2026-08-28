#!/usr/bin/env python3
"""投稿停止の監視。本日(JST)の親投稿数が基準未満なら異常終了する。
GitHub Actionsのジョブ失敗として検知され、リポジトリ所有者へ通知メールが飛ぶ。"""
import os, json, time, urllib.request, urllib.parse, sys
from datetime import datetime, timezone, timedelta
API = "https://graph.threads.net/v1.0"
JST = timezone(timedelta(hours=9))
UID = os.environ["THREADS_USER_ID"]
Q = urllib.parse.quote(os.environ["THREADS_ACCESS_TOKEN"])
MIN = int(os.environ.get("MIN_POSTS", "1"))
ACCT = os.environ.get("ACCOUNT", "?")
d = json.loads(urllib.request.urlopen(
    f"{API}/{UID}/threads?fields=timestamp,is_reply&since={int(time.time())-86400}&limit=100&access_token=" + Q,
    timeout=30).read())
today = datetime.now(JST).strftime("%Y-%m-%d")
n = sum(1 for p in d.get("data", [])
        if not p.get("is_reply")
        and datetime.strptime(p["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(JST).strftime("%Y-%m-%d") == today)
print(f"[{ACCT}] 本日の投稿 {n}本 (基準 {MIN}本)")
if n < MIN:
    print(f"[{ACCT}] ⚠️ 投稿が止まっています！", file=sys.stderr)
    sys.exit(1)
