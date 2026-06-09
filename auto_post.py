#!/usr/bin/env python3
"""
ゴールデンタイム自動投稿（アカウント1: koshigaya_diet_seitai）
- content_bank.json からツリーを巡回で取り出して投稿
- 1回の起動で1ツリー投稿（cronで時刻ごとに起動する想定）
- 投稿ログを post_log.jsonl に記録
- state.json で次に投稿するインデックスと当日カウントを管理
"""
import os, json, time, urllib.request, urllib.parse, sys
from datetime import datetime, timezone, timedelta

API = "https://graph.threads.net/v1.0"
DIR = os.path.dirname(os.path.abspath(__file__))
JST = timezone(timedelta(hours=9))
DAILY_CAP = 35  # 1日の上限ツリー数

UID = os.environ["THREADS_USER_ID"]
TOK = os.environ["THREADS_ACCESS_TOKEN"]


def post(path, params):
    params["access_token"] = TOK
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(f"{API}/{path}", data=data, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def publish_tree(segments):
    prev = None
    ids = []
    for text in segments:
        p = {"media_type": "TEXT", "text": text}
        if prev:
            p["reply_to_id"] = prev
        cid = post(f"{UID}/threads", p)["id"]
        time.sleep(2)
        pid = post(f"{UID}/threads_publish", {"creation_id": cid})["id"]
        ids.append(pid)
        prev = pid
        time.sleep(2)
    return ids


def load(name, default):
    p = os.path.join(DIR, name)
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return default


def save(name, obj):
    json.dump(obj, open(os.path.join(DIR, name), "w"), ensure_ascii=False, indent=1)


def main():
    bank = load("content_bank.json", [])
    if not bank:
        print("バンクが空です"); return
    state = load("state.json", {"idx": 0, "day": "", "count": 0})
    today = datetime.now(JST).strftime("%Y-%m-%d")
    if state["day"] != today:
        state["day"] = today
        state["count"] = 0
    if state["count"] >= DAILY_CAP:
        print(f"本日の上限({DAILY_CAP})に到達。スキップ。")
        return

    tree = bank[state["idx"] % len(bank)]
    segs = tree["segments"]
    try:
        ids = publish_tree(segs)
        # ログ
        rec = {"ts": datetime.now(JST).isoformat(), "bank_idx": state["idx"] % len(bank),
               "type": tree.get("type"), "post_ids": ids, "first_id": ids[0],
               "hook": segs[0][:40]}
        with open(os.path.join(DIR, "post_log.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        state["idx"] += 1
        state["count"] += 1
        save("state.json", state)
        print(f"投稿成功 [{state['count']}/{DAILY_CAP}] type={tree.get('type')} first_id={ids[0]}")
    except Exception as e:
        print(f"投稿失敗: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
