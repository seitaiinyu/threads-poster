#!/usr/bin/env python3
"""2026-11-21 分析結果に基づく修正。
A1: 深夜(0-5時)の投稿を止める / 反応の弱い「人柄・哲学」型を朝の優先枠から外す
A2: 重複防止を48h→7日に延長 / 3回出て全て100表示未満だった投稿を削除"""
import json, os, re
DIR = os.path.dirname(os.path.abspath(__file__))

# --- auto_post.py ---
p = os.path.join(DIR, "auto_post.py")
s = open(p, encoding="utf-8").read()
old = """        elif hour < 3:
            target = cap         # 深夜0-2時は前日の最終キャッチアップ
        else:
            target = 0"""
new = """        else:
            target = 0           # 深夜0-5時は投稿しない(表示が伸びず、連投扱いにもなる)"""
assert old in s, "A1 深夜ブロックが見つからない"
s = s.replace(old, new)
old2 = '"local_every": 4, "disease_rotate": True, "shindan_weekdays": [0,1,2,3,4,5,6], "shindan_slots": [0, 14]}'
new2 = '"local_every": 4, "disease_rotate": True, "shindan_weekdays": [0,1,2,3,4,5,6], "shindan_slots": [0, 14], "dedup_hours": 168}'
assert old2 in s, "A2 設定が見つからない"
s = s.replace(old2, new2)
open(p, "w", encoding="utf-8").write(s)
import ast; ast.parse(s)
print("auto_post.py: A1深夜停止 / A2重複防止7日")

# --- A1: 人柄・哲学型を朝優先から外す(type live→philo) ---
p = os.path.join(DIR, "content_bank.json")
b = json.load(open(p, encoding="utf-8"))
k = 0
for t in b:
    if t.get("type") == "live" and t.get("cat") == "personality":
        t["type"] = "philo"; k += 1
json.dump(b, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"A1: 人柄型 {k}本を朝の優先枠から外した(夜枠では引き続き配信)")

# --- A2: 弱い常連を削除 ---
p = os.path.join(DIR, "content_bank_yu.json")
b = json.load(open(p, encoding="utf-8"))
WEAK = ("このまま何年も通い続けるのか", "腰痛のストレッチで、")
before = len(b)
b = [t for t in b if not any(t["segments"][0].startswith(w) for w in WEAK)]
json.dump(b, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"A2: 弱い投稿 {before-len(b)}本を削除 / 計{len(b)}")
