#!/usr/bin/env python3
"""アカウント2（koshigaya_seitai_yu）の過去投稿を閲覧数でランキングし、
高パフォーマンスの“勝ちネタ”を改良候補として抽出する。
- 既に改良済み（harvested_yu.json に記録）の元投稿は除外＝重複防止
- 結果を candidates_yu.json に出力（私がこれを見てツリーに改良→バンク追加）
"""
import os, json, time, urllib.request, urllib.parse, sys
from datetime import datetime, timezone, timedelta

API = "https://graph.threads.net/v1.0"
DIR = os.path.dirname(os.path.abspath(__file__))
JST = timezone(timedelta(hours=9))
UID = os.environ["THREADS_USER_ID"]
TOK = os.environ["THREADS_ACCESS_TOKEN"]

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 30
TOP_K = 30


def get(url):
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read().decode())


def fetch_posts(days):
    since = int(time.time()) - days * 86400
    url = f"{API}/{UID}/threads?fields=id,text,timestamp,media_type&since={since}&limit=100&access_token=" + urllib.parse.quote(TOK)
    posts = []
    pages = 0
    while url and pages < 40:
        d = get(url)
        posts.extend(d.get("data", []))
        url = d.get("paging", {}).get("next")
        pages += 1
    return posts


def views(mid):
    url = f"{API}/{mid}/insights?metric=views&access_token=" + urllib.parse.quote(TOK)
    try:
        d = get(url)
        for m in d.get("data", []):
            if m["name"] == "views":
                v = m.get("values", [{}])
                return v[0].get("value", 0) if v else 0
    except Exception:
        return None
    return 0


def main():
    harvested = set(json.load(open(os.path.join(DIR, "harvested_yu.json"))) ) if os.path.exists(os.path.join(DIR, "harvested_yu.json")) else set()
    posts = fetch_posts(DAYS)
    # 親投稿っぽいTEXT/IMAGEのみ、未改良のみ、本文ありのみ
    posts = [p for p in posts if p.get("media_type") in ("TEXT_POST", "IMAGE")
             and p.get("text") and p["id"] not in harvested]
    print(f"対象候補: {len(posts)}件（{DAYS}日間, 未改良）", flush=True)

    scored = []
    log = open(os.path.join(DIR, "harvest_progress.txt"), "w")
    for i, p in enumerate(posts, 1):
        v = views(p["id"])
        if v is not None:
            scored.append({"id": p["id"], "text": p["text"], "ts": p["timestamp"], "views": v})
        if i % 100 == 0:
            log.write(f"{i}/{len(posts)}\n"); log.flush()
        time.sleep(0.03)

    scored.sort(key=lambda x: -x["views"])
    top = scored[:TOP_K]
    json.dump(top, open(os.path.join(DIR, "candidates_yu.json"), "w"), ensure_ascii=False, indent=1)

    print(f"\n=== 改良候補トップ{len(top)}（閲覧数順）===")
    for i, c in enumerate(top, 1):
        t = c["text"].replace("\n", " ")[:50]
        print(f"{i:>2}. {c['views']:>6} views | {t}")


if __name__ == "__main__":
    main()
