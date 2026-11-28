#!/usr/bin/env python3
"""越谷あるある型(type=local2, local=True)の下書きを両バンクへ追加。 usage: python3 add_local.py"""
import json, os, re
DIR = os.path.dirname(os.path.abspath(__file__))
BAN = re.compile(r"http|lin\.ee|必ず治|100%|方へ|人へ|のです|しましょう|すべき")


def merge(draft_name, bank_name, is_yu):
    dp = os.path.join(DIR, draft_name)
    if not os.path.exists(dp):
        print("下書きなし:", draft_name); return
    draft = json.load(open(dp, encoding="utf-8"))
    bp = os.path.join(DIR, bank_name)
    bank = json.load(open(bp, encoding="utf-8"))
    ex = {t["segments"][0].split("\n")[0].strip() for t in bank}
    n = skipped = 0
    for d in draft:
        segs = [s.strip() for s in d["segments"]]
        hook = segs[0].split("\n")[0].strip()
        if hook in ex or "越谷" not in segs[0]:
            print("除外(重複/越谷なし):", hook); skipped += 1; continue
        if any(BAN.search(s) for s in segs) or len(segs[0].replace("\n", "")) > 44:
            print("除外(禁止語/長さ):", hook); skipped += 1; continue
        t = {"type": "local2", "cat": "local", "local": True, "segments": segs}
        if is_yu:
            t["disease"] = d.get("disease", "腰痛")
        else:
            t["cta"] = ""
            if d.get("cta") == "shindan" or "固定投稿" in segs[-1]:
                t["shindan"] = True
        if d.get("until"):
            t["until"] = d["until"]
        bank.append(t); ex.add(hook); n += 1
    json.dump(bank, open(bp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{bank_name}: 追加 {n} / 除外 {skipped} / 計 {len(bank)}")


if __name__ == "__main__":
    merge("draft_local_diet.json", "content_bank.json", False)
    merge("draft_local_yu.json", "content_bank_yu.json", True)
