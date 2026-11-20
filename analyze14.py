#!/usr/bin/env python3
"""直近14日の親投稿をAPIから取得し、日別・時間帯別・型別・TOP/WORSTを表示する。
環境変数 THREADS_USER_ID / THREADS_ACCESS_TOKEN / LABEL を使う。"""
import os, json, time, urllib.request, urllib.parse, statistics as st, re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from collections import defaultdict

API = "https://graph.threads.net/v1.0"
UID = os.environ["THREADS_USER_ID"]
Q = urllib.parse.quote(os.environ["THREADS_ACCESS_TOKEN"])
LABEL = os.environ.get("LABEL", "")
JST = timezone(timedelta(hours=9))


def get(u):
    return json.loads(urllib.request.urlopen(u, timeout=30).read().decode())


since = int(time.time()) - 14 * 86400
url = f"{API}/{UID}/threads?fields=id,text,timestamp,is_reply&since={since}&limit=100&access_token=" + Q
posts, pages = [], 0
while url and pages < 10:
    d = get(url)
    posts += [p for p in d.get("data", []) if not p.get("is_reply")]
    url = d.get("paging", {}).get("next"); pages += 1


def ins(p):
    try:
        m = {x["name"]: x.get("values", [{}])[0].get("value", 0)
             for x in get(f"{API}/{p['id']}/insights?metric=views,likes,replies&access_token=" + Q)["data"]}
        ts = datetime.strptime(p["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(JST)
        return (ts, p["text"].split("\n")[0][:36], m.get("views", 0), m.get("likes", 0), m.get("replies", 0), p["text"])
    except Exception:
        return None


with ThreadPoolExecutor(12) as ex:
    rows = [r for r in ex.map(ins, posts) if r]
rows.sort(key=lambda r: r[0])

print(f"===== {LABEL} =====")
print("親投稿", len(rows))
try:
    f = get(f"{API}/{UID}/threads_insights?metric=followers_count&access_token=" + Q)
    print("フォロワー:", f["data"][0].get("total_value", {}).get("value"))
except Exception:
    pass

print("\n--- 日別 ---")
d = defaultdict(list)
for r in rows:
    d[r[0].strftime("%m/%d")].append(r)
for k in sorted(d):
    v = d[k]
    print(f"{k} {len(v):2d}本 表示計{sum(x[2] for x in v):6d} 中央{int(st.median([x[2] for x in v])):5d} ♥{sum(x[3] for x in v):3d}")

print("\n--- 時間帯別 ---")
h = defaultdict(list)
for r in rows:
    h[r[0].hour].append(r)
for k in sorted(h):
    v = h[k]
    print(f"{k:2d}時 {len(v):3d}本 中央{int(st.median([x[2] for x in v])):5d}")

print("\n--- 診断/LINE誘導つき vs なし ---")
cta = [r for r in rows if re.search(r"固定投稿|診断|LINE", r[5])]
non = [r for r in rows if r not in cta]
if cta:
    print(f"誘導あり {len(cta)}本 中央{int(st.median([x[2] for x in cta]))}")
if non:
    print(f"誘導なし {len(non)}本 中央{int(st.median([x[2] for x in non]))}")

print("\n--- TOP8 ---")
for r in sorted(rows, key=lambda r: -r[2])[:8]:
    print(f"{r[2]:6d} ♥{r[3]:3d} 💬{r[4]:3d} | {r[0].strftime('%m/%d %H時')} {r[1]}")
print("\n--- WORST5 ---")
for r in sorted(rows, key=lambda r: r[2])[:5]:
    print(f"{r[2]:6d} | {r[0].strftime('%m/%d %H時')} {r[1]}")

v = [x[2] for x in rows]
if v:
    first = [x[2] for x in rows if x[0] < rows[0][0] + timedelta(days=7)]
    last = [x[2] for x in rows if x[0] >= rows[0][0] + timedelta(days=7)]
    print(f"\n全体: 中央値{int(st.median(v))} 合計{sum(v)} 総♥{sum(x[3] for x in rows)}")
    if first and last:
        print(f"前半7日 中央{int(st.median(first))} → 後半7日 中央{int(st.median(last))}")
