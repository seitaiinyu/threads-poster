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
    # 回復最優先: 1日4本の少量・質重視運用（正常な投稿頻度でスパム判定を回避）
    "diet": {"bank": "content_bank.json",    "state": "state.json",    "log": "post_log.jsonl",    "cap": 4,  "from": "2026-06-11", "cta_every": 0, "batch": 4,  "spacing": 600, "local_every": 2},
    # local_every: N投稿に1本を地域特化(local=True)にする（商圏向け）。地域投稿のCTAは2回に1回
    "yu":   {"bank": "content_bank_yu.json", "state": "state_yu.json", "log": "post_log_yu.jsonl", "cap": 30, "from": "2026-06-11", "cta_every": 4, "batch": 30, "spacing": 120, "local_every": 4},
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


def fetch_recent(hours=48):
    """直近の自分の親投稿から、(フック集合, 当日(JST)の親投稿数) を返す。
    Git状態に依存せず、重複防止と当日上限の両方をAPI実データで担保する。"""
    since = int(time.time()) - hours * 3600
    url = (f"{API}/{UID}/threads?fields=text,timestamp,is_reply&since={since}"
           f"&limit=100&access_token=" + urllib.parse.quote(TOK))
    hooks = set()
    today = datetime.now(JST).strftime("%Y-%m-%d")
    today_count = 0
    pages = 0
    while url and pages < 10:
        try:
            d = json.loads(urllib.request.urlopen(url).read().decode())
        except Exception:
            break
        for p in d.get("data", []):
            if p.get("is_reply") or not p.get("text"):
                continue
            hooks.add(p["text"].split("\n")[0].strip())
            ts = datetime.strptime(p["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(JST)
            if ts.strftime("%Y-%m-%d") == today:
                today_count += 1
        url = d.get("paging", {}).get("next")
        pages += 1
    return hooks, today_count


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


def hook_of(tree):
    return tree["segments"][0].split("\n")[0].strip()


# 曜日(月=0〜日=6) → 投稿の型。金=動線。土=共感、日=事例。
CATEGORY_BY_WEEKDAY = {
    0: "empathy", 1: "education", 2: "case", 3: "personality",
    4: "funnel", 5: "empathy", 6: "case",
}


def today_category():
    wd = datetime.now(JST).weekday()
    cat = CATEGORY_BY_WEEKDAY[wd]
    # 回復期のアカウント1は動線(CTA)を出さない → 教育に振替
    if ACCT == "diet" and cat == "funnel" and CFG.get("cta_every", 1) == 0:
        cat = "education"
    return cat


def post_one(bank, state, cap, seen, target_cat, want_local=False):
    """1ツリー投稿。地域回(want_local)は地域投稿を優先、通常回は今日の型を優先。重複(seen)回避。"""
    n = len(bank)
    pick = None
    # ⓪ 地域回: local=True かつ 未投稿 を最優先
    if want_local:
        for off in range(n):
            t = bank[(state["idx"] + off) % n]
            if t.get("local") and hook_of(t) not in seen:
                pick = (state["idx"] + off) % n; break
    # ① 今日の型 かつ 未投稿
    if pick is None:
        for off in range(n):
            t = bank[(state["idx"] + off) % n]
            if t.get("cat") == target_cat and hook_of(t) not in seen:
                pick = (state["idx"] + off) % n; break
    # ② 無ければ 型不問で未投稿
    if pick is None:
        for off in range(n):
            t = bank[(state["idx"] + off) % n]
            if hook_of(t) not in seen:
                pick = (state["idx"] + off) % n; break
    if pick is None:
        print(f"[{ACCT}] 全ツリーが直近投稿済み。スキップ。")
        return False
    state["idx"] = pick
    tree = bank[state["idx"] % len(bank)]
    segs = list(tree["segments"])
    cta_every = CFG.get("cta_every", 1)
    cta_turn = cta_every > 0 and (state["count"] % cta_every == 0)
    if tree.get("local"):
        # 地域投稿: 最終段がCTA(プロフィール誘導)の場合のみ、2回に1回だけCTAを外す。
        # CTAなしの地域投稿(回復期A1の純価値提供)はそのまま3段で出す。
        last = segs[-1] if segs else ""
        is_cta = "プロフィール" in last
        if is_cta and len(segs) >= 2 and state["count"] % 2 == 1:
            segs = segs[:-1]
    elif "cta" in tree:
        # 3部構成: ③は通常「まとめ」。CTA回は③をCTAに置換（常に3投稿）
        if cta_turn:
            segs = segs[:2] + [tree["cta"]]
    else:
        # 旧形式: CTAは最終段。非CTA回は外す
        if len(segs) >= 2 and (cta_every == 0 or (cta_every > 1 and not cta_turn)):
            segs = segs[:-1]
    ids = publish_tree(segs)
    rec = {"ts": datetime.now(JST).isoformat(), "bank_idx": state["idx"] % len(bank),
           "type": tree.get("type"), "post_ids": ids, "first_id": ids[0],
           "hook": segs[0][:40]}
    with open(os.path.join(DIR, CFG["log"]), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    seen.add(hook_of(tree))
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

    # 重複防止＋当日上限: API実データから直近フックと当日投稿数を取得
    seen, today_count = fetch_recent(48)
    # 当日数はAPI実数と状態の大きい方を採用（Git状態が失われても過剰投稿しない）
    state["count"] = max(state["count"], today_count)

    # キャッチアップ方式: 1回あたり batch 本まで、当日 cap まで。
    batch = CFG.get("batch", 1)
    spacing = CFG.get("spacing", 240)  # 投稿間の待機秒
    remaining = cap - state["count"]
    n = min(batch, remaining)
    if n <= 0:
        print(f"[{ACCT}] 本日の上限({cap})に到達済み（実投稿{today_count}）。スキップ。")
        return
    cat = today_category()
    print(f"[{ACCT}] このランで最大{n}本投稿（本日 {state['count']}/{cap}, 型={cat}, 直近{len(seen)}種回避）")
    local_every = CFG.get("local_every", 0)
    posted = 0
    for i in range(n):
        want_local = local_every > 0 and (state["count"] % local_every == 1)
        try:
            ok = post_one(bank, state, cap, seen, cat, want_local)
            if not ok:
                break
            posted += 1
        except Exception as e:
            print(f"[{ACCT}] 投稿失敗: {e}", file=sys.stderr)
            sys.exit(1)
        if i < n - 1:
            time.sleep(spacing)


if __name__ == "__main__":
    main()
