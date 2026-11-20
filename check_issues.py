#!/usr/bin/env python3
"""分析で見つかった疑問点の裏取り。
1) A1: 直近14日の投稿ログに診断(shindan)投稿があるか / 型別の内訳
2) A2: 直近14日で3回以上出た同一フックと、その平均表示（弱い常連の洗い出し）"""
import json, os, re, statistics as st
from datetime import datetime, timedelta, timezone
from collections import defaultdict, Counter

DIR = os.path.dirname(os.path.abspath(__file__))
JST = timezone(timedelta(hours=9))
cut = datetime.now(JST) - timedelta(days=14)

print("=== A1 投稿ログ(14日) 型別 ===")
bank = json.load(open(os.path.join(DIR, "content_bank.json"), encoding="utf-8"))
types = Counter(); sh = 0; cnt = 0
for line in open(os.path.join(DIR, "post_log.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    ts = datetime.fromisoformat(r["ts"])
    if ts < cut:
        continue
    cnt += 1
    types[r.get("type")] += 1
    idx = r.get("bank_idx")
    if idx is not None and idx < len(bank) and bank[idx].get("shindan"):
        sh += 1
print("自動投稿", cnt, "本 / 診断投稿", sh, "本")
print(types.most_common())
print("診断投稿の在庫:", sum(1 for t in bank if t.get("shindan")), "本")
print("直近3件のログ:")
for line in open(os.path.join(DIR, "post_log.jsonl"), encoding="utf-8").readlines()[-3:]:
    r = json.loads(line); print(" ", r["ts"][:16], r.get("type"), r.get("hook", "")[:30])

print("\n=== A2 設定 ===")
import importlib.util
src = open(os.path.join(DIR, "auto_post.py"), encoding="utf-8").read()
m = re.search(r'"yu":\s*\{[^}]*\}', src)
print(m.group(0)[:300] if m else "not found")
