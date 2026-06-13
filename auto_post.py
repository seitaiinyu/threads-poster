#!/usr/bin/env python3
"""
ゴールデンタイム自動投稿（両アカウント対応）
- 環境変数 ACCOUNT で対象を切替（"diet"=koshigaya_diet_seitai / "yu"=koshigaya_seitai_yu）
- content_bank_<acct>.json からツリーを巡回で取り出して1ツリー投稿
- 投稿ログを post_log_<acct>.jsonl、進捗を state_<acct>.json に記録
- UID/TOKEN は環境変数 THREADS_USER_ID / THREADS_ACCESS_TOKEN（ワークフローが各アカウントのSecretを渡す）
"""
import os, json, time, urllib.request, urllib.parse, sys
from datetime import datetime, timezone, timedelta

API = "https://graph.threads.net/v1.0"
DIR = os.path.dirname(os.path.abspath(__file__))
JST = timezone(timedelta(hours=9))

# アカウント別設定
# cap: 1日の上限ツリー数 / cta_every: 何投稿に1回CTAを入れるか（1=毎回）
CONFIG = {
    # アカウント1はリーチ制限からの回復のため少量・CTA控えめ
    # batch: 1回の起動で投稿する最大本数（キャッチアップ用） / spacing: 投稿間隔(秒)
    "diet": {"bank": "content_bank.json",    "state": "state.json",    "log": "post_log.jsonl",    "cap": 7,  "from": "2026-06-11", "cta_every": 0, "batch": 7,  "spacing": 300},
    "yu":   {"bank": "content_bank_yu.json", "state": "state_yu.json", "log": "post_log_yu.jsonl", "cap": 30, "from": "2026-06-11", "cta_every": 4, "batch": 30, "spacing": 120},
}

ACCT = os.environ.get("ACCOUNT", "diet")
CFG = CONFIG[ACCT]
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


def post_one(bank, state, cap):
    """1ツリー投稿。成功でTrue。"""
    tree = bank[state["idx"] % len(bank)]
    segs = list(tree["segments"])
    cta_every = CFG.get("cta_every", 1)
    if len(segs) >= 2 and (cta_every == 0 or (cta_every > 1 and state["count"] % cta_every != 0)):
        segs = segs[:-1]  # 最終段(CTA)を除外（cta_every=0は常にCTAなし＝回復期）
    ids = publish_tree(segs)
    rec = {"ts": datetime.now(JST).isoformat(), "bank_idx": state["idx"] % len(bank),
           "type": tree.get("type"), "post_ids": ids, "first_id": ids[0],
           "hook": segs[0][:40]}
    with open(os.path.join(DIR, CFG["log"]), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    state["idx"] += 1
    state["count"] += 1
    save(CFG["state"], state)
    print(f"[{ACCT}] 投稿成功 [{state['count']}/{cap}] type={tree.get('type')} first_id={ids[0]}")
    return True


def main():
    today = datetime.now(JST).strftime("%Y-%m-%d")
    if today < CFG["from"]:
        print(f"[{ACCT}] 稼働開始日({CFG['from']})前のためスキップ（本日 {today}）")
        return
    bank = load(CFG["bank"], [])
    if not bank:
        print(f"[{ACCT}] バンクが空です"); return
    state = load(CFG["state"], {"idx": 0, "day": "", "count": 0})
    if state["day"] != today:
        state["day"] = today
        state["count"] = 0
    cap = CFG["cap"]

    # キャッチアップ方式: GitHubの発火が間引かれても、この1回でその時点の不足分を
    # まとめて投稿（数分間隔）。1回あたり batch 本まで、当日 cap まで。
    batch = CFG.get("batch", 1)
    spacing = CFG.get("spacing", 240)  # 投稿間の待機秒
    remaining = cap - state["count"]
    n = min(batch, remaining)
    if n <= 0:
        print(f"[{ACCT}] 本日の上限({cap})に到達済み。スキップ。")
        return
    print(f"[{ACCT}] このランで最大{n}本投稿（本日 {state['count']}/{cap}）")
    for i in range(n):
        try:
            post_one(bank, state, cap)
        except Exception as e:
            print(f"[{ACCT}] 投稿失敗: {e}", file=sys.stderr)
            sys.exit(1)
        if i < n - 1:
            time.sleep(spacing)


if __name__ == "__main__":
    main()
