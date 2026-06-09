#!/usr/bin/env python3
"""過去90日の投稿を時間帯別に分析（JST）。閲覧数で評価。"""
import os, json, time, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

API = "https://graph.threads.net/v1.0"
UID = os.environ["THREADS_USER_ID"]
TOK = os.environ["THREADS_ACCESS_TOKEN"]
JST = timezone(timedelta(hours=9))


def get(url):
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read().decode())


def fetch_all_posts(days=90):
    since = int(time.time()) - days * 86400
    url = f"{API}/{UID}/threads?fields=id,timestamp,media_type&since={since}&limit=100&access_token={urllib.parse.quote(TOK)}"
    posts = []
    while url:
        d = get(url)
        posts.extend(d.get("data", []))
        url = d.get("paging", {}).get("next")
        if len(posts) > 2000:
            break
    return posts


def fetch_views(media_id):
    url = f"{API}/{media_id}/insights?metric=views&access_token={urllib.parse.quote(TOK)}"
    try:
        d = get(url)
        for m in d.get("data", []):
            if m["name"] == "views":
                v = m.get("values", [{}])
                if v and "value" in v[0]:
                    return v[0]["value"]
                return m.get("total_value", {}).get("value", 0)
    except Exception:
        return None
    return 0


def main():
    posts = fetch_all_posts(90)
    print(f"総投稿数(90日): {len(posts)}")
    rows = []
    for i, p in enumerate(posts, 1):
        # 親投稿のみ（返信ツリーの子も含むが、ここでは全件対象）
        ts = datetime.strptime(p["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(JST)
        views = fetch_views(p["id"])
        if views is None:
            continue
        rows.append((ts.hour, ts.weekday(), views))
        if i % 50 == 0:
            print(f"  ...{i}件処理")
        time.sleep(0.05)

    # 時間帯バケツ
    from collections import defaultdict
    hour_views = defaultdict(list)
    for h, wd, v in rows:
        hour_views[h].append(v)

    print(f"\n分析対象(閲覧数取得成功): {len(rows)}件\n")
    print("=== 時間帯別 平均閲覧数（JST）===")
    print(f"{'時間':>5} | {'投稿数':>5} | {'平均閲覧':>8} | {'中央値':>7} | {'最大':>7}")
    import statistics
    summary = []
    for h in range(24):
        vs = hour_views.get(h, [])
        if not vs:
            continue
        avg = statistics.mean(vs)
        med = statistics.median(vs)
        summary.append((h, len(vs), avg, med, max(vs)))
    # 平均閲覧で降順
    for h, n, avg, med, mx in sorted(summary, key=lambda x: -x[2]):
        bar = "█" * int(avg / max(1, max(s[2] for s in summary)) * 30)
        print(f"{h:>3}時 | {n:>5} | {avg:>8.0f} | {med:>7.0f} | {mx:>7} {bar}")

    # 3時間帯ブロック
    print("\n=== 時間ブロック別 平均閲覧数 ===")
    blocks = {"早朝 5-8時":range(5,9),"午前 9-11時":range(9,12),"昼 12-14時":range(12,15),
              "午後 15-17時":range(15,18),"夜 18-21時":range(18,22),"深夜 22-4時":list(range(22,24))+list(range(0,5))}
    bl = []
    for name, hrs in blocks.items():
        vs = [v for h in hrs for v in hour_views.get(h, [])]
        if vs:
            bl.append((name, len(vs), statistics.mean(vs)))
    for name, n, avg in sorted(bl, key=lambda x:-x[2]):
        print(f"{name:>12}: 投稿{n:>4}件  平均閲覧 {avg:>8.0f}")


if __name__ == "__main__":
    main()
