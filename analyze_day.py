#!/usr/bin/env python3
"""その日に自動投稿したツリーの成果を集計してレポート化（アカウント1）。"""
import os, json, time, urllib.request, urllib.parse, statistics, sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict

API = "https://graph.threads.net/v1.0"
DIR = os.path.dirname(os.path.abspath(__file__))
JST = timezone(timedelta(hours=9))
TOK = os.environ["THREADS_ACCESS_TOKEN"]
ACCT = os.environ.get("ACCOUNT", "diet")
LOGFILE = "post_log_yu.jsonl" if ACCT == "yu" else "post_log.jsonl"
ACCT_LABEL = "koshigaya_seitai_yu" if ACCT == "yu" else "koshigaya_diet_seitai"


def insights(mid):
    url = f"{API}/{mid}/insights?metric=views,likes,replies&access_token=" + urllib.parse.quote(TOK)
    try:
        with urllib.request.urlopen(url) as r:
            d = json.loads(r.read().decode())
        out = {}
        for m in d.get("data", []):
            v = m.get("values", [{}])
            out[m["name"]] = v[0].get("value", 0) if v else 0
        return out
    except Exception:
        return {}


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else datetime.now(JST).strftime("%Y-%m-%d")
    logp = os.path.join(DIR, LOGFILE)
    if not os.path.exists(logp):
        print("ログがありません"); return
    recs = []
    for line in open(logp, encoding="utf-8"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r["ts"][:10] == day:
            recs.append(r)
    if not recs:
        print(f"{day} の投稿記録がありません"); return

    rows = []
    for r in recs:
        ins = insights(r["first_id"])
        hour = datetime.fromisoformat(r["ts"]).astimezone(JST).hour
        rows.append({"hour": hour, "type": r.get("type"), "bank_idx": r.get("bank_idx"),
                     "hook": r.get("hook", ""), "views": ins.get("views", 0),
                     "likes": ins.get("likes", 0), "replies": ins.get("replies", 0)})
        time.sleep(0.05)

    out = []
    out.append(f"===== 日次レポート {day}（{ACCT_LABEL}）=====")
    out.append(f"投稿ツリー数: {len(rows)}")
    tv = sum(x["views"] for x in rows); tl = sum(x["likes"] for x in rows); tr = sum(x["replies"] for x in rows)
    out.append(f"合計閲覧: {tv:,}  合計いいね: {tl}  合計返信: {tr}")
    if rows:
        out.append(f"平均閲覧: {tv/len(rows):.0f}  いいね率: {(tl/tv*100 if tv else 0):.2f}%")

    # 時間帯別
    out.append("\n--- 時間帯別 平均閲覧 ---")
    hv = defaultdict(list)
    for x in rows: hv[x["hour"]].append(x["views"])
    for h in sorted(hv, key=lambda h: -statistics.mean(hv[h])):
        out.append(f"{h:>2}時: {len(hv[h]):>2}本  平均閲覧 {statistics.mean(hv[h]):>6.0f}")

    # タイプ別
    out.append("\n--- コンテンツタイプ別 ---")
    tvd = defaultdict(list)
    for x in rows: tvd[x["type"]].append(x["views"])
    for t, vs in tvd.items():
        out.append(f"{t}: {len(vs)}本  平均閲覧 {statistics.mean(vs):.0f}")

    # トップ5・ワースト5
    srt = sorted(rows, key=lambda x: -x["views"])
    out.append("\n--- 閲覧トップ5 ---")
    for x in srt[:5]:
        out.append(f"  {x['views']:>6} views | L{x['likes']} R{x['replies']} | {x['hook']}")
    out.append("\n--- 閲覧ワースト5 ---")
    for x in srt[-5:]:
        out.append(f"  {x['views']:>6} views | L{x['likes']} R{x['replies']} | {x['hook']}")

    res = "\n".join(out)
    open(os.path.join(DIR, f"daily_report_{ACCT}_{day}.txt"), "w", encoding="utf-8").write(res)
    print(res)


if __name__ == "__main__":
    main()
