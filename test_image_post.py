#!/usr/bin/env python3
"""画像つき事例ツリーを1本だけ本番投稿して、画像投稿の経路を確認する。
投稿したツリーは post_log.jsonl に記録し、7日間の重複防止に乗せる。"""
import os, json, sys
from datetime import datetime
os.environ.setdefault("ACCOUNT", "diet")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auto_post as ap

bank = ap.load(ap.CFG["bank"], [])
cases = [(i, t) for i, t in enumerate(bank) if t.get("type") == "case2" and t.get("image")]
idx, tree = cases[8]  # ヨガ・パーソナルでもリバウンド → −13.8kg
print("投稿:", tree["segments"][0].replace("\n", " / "), "/ 画像:", tree["image"])
ids = ap.publish_tree(tree["segments"], tree["image"])
rec = {"ts": datetime.now(ap.JST).isoformat(), "bank_idx": idx, "type": "case2",
       "post_ids": ids, "first_id": ids[0], "hook": tree["segments"][0][:40]}
with open(os.path.join(ap.DIR, ap.CFG["log"]), "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("成功 first_id=", ids[0], "投稿数", len(ids))
