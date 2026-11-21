#!/usr/bin/env python3
"""直近の親投稿3件について、ツリーの返信(2投稿目以降)の本文を取得し、
1行の最大文字数・改行数を表示する。環境変数 THREADS_USER_ID / THREADS_ACCESS_TOKEN。"""
import os, json, time, urllib.request, urllib.parse
API = "https://graph.threads.net/v1.0"
UID = os.environ["THREADS_USER_ID"]
Q = urllib.parse.quote(os.environ["THREADS_ACCESS_TOKEN"])


def get(u):
    return json.loads(urllib.request.urlopen(u, timeout=30).read().decode())


d = get(f"{API}/{UID}/threads?fields=id,text,timestamp,is_reply&since={int(time.time())-6*3600}&limit=20&access_token=" + Q)
parents = [p for p in d.get("data", []) if not p.get("is_reply")][:3]
for p in parents:
    print("=" * 40)
    print("①", p["text"][:60].replace("\n", " / "))
    r = get(f"{API}/{p['id']}/replies?fields=id,text&access_token=" + Q)
    for i, rep in enumerate(r.get("data", []), start=2):
        t = rep.get("text", "")
        lines = t.split("\n")
        print(f"[{i}投稿目] 行数{len(lines)} 最長行{max(len(l) for l in lines)}文字")
        print(t)
        print("--")
        # 3投稿目はこの返信の返信
        r2 = get(f"{API}/{rep['id']}/replies?fields=id,text&access_token=" + Q)
        for j, rep2 in enumerate(r2.get("data", []), start=3):
            t2 = rep2.get("text", "")
            l2 = t2.split("\n")
            print(f"[{j}投稿目] 行数{len(l2)} 最長行{max(len(l) for l in l2)}文字")
            print(t2)
            print("--")
