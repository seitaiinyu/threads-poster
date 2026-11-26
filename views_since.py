#!/usr/bin/env python3
"""指定日以降のA1投稿の表示数を、画像あり/なし・型ごとに集計する。 usage: python3 views_since.py 2026-11-22"""
import os, sys, json, statistics, urllib.request, urllib.parse
DIR = os.path.dirname(os.path.abspath(__file__))
for line in open(os.path.join(DIR, ".env"), encoding="utf-8"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1); os.environ.setdefault(k, v.strip().strip('"'))
TOK = os.environ["THREADS_ACCESS_TOKEN"]
since = sys.argv[1]
bank = json.load(open(os.path.join(DIR, "content_bank.json"), encoding="utf-8"))
rows = []
for line in open(os.path.join(DIR, "post_log.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    if r["ts"][:10] < since:
        continue
    pid = r.get("first_id") or r["post_ids"][0]
    q = urllib.parse.urlencode({"metric": "views,likes,replies", "access_token": TOK})
    try:
        d = json.load(urllib.request.urlopen(f"https://graph.threads.net/v1.0/{pid}/insights?{q}"))
        m = {x["name"]: x["values"][0]["value"] for x in d["data"]}
    except Exception as e:
        m = {"views": -1}
    t = bank[r["bank_idx"]] if r.get("bank_idx") is not None and r["bank_idx"] < len(bank) else {}
    img = r.get("image_used", bool(t.get("image")) or r.get("type") == "case2")
    rows.append((r["ts"][5:16], r.get("type"), "画像" if img else "文字", m.get("views", -1), m.get("likes", 0), r.get("hook", "")[:28]))
for x in sorted(rows):
    print(*x, sep=" | ")
for lab in ("画像", "文字"):
    vs = [x[3] for x in rows if x[2] == lab and x[3] >= 0]
    if vs:
        print(f"{lab}: {len(vs)}本 中央値{int(statistics.median(vs))} 平均{int(sum(vs)/len(vs))} 最大{max(vs)}")
