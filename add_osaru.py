#!/usr/bin/env python3
"""OSARU 8型（ninchi/hozon/kyokan/hanten/jisseki/kyoiku）の下書きを両バンクに追加し、
朝の優先枠にも加える。 usage: python3 add_osaru.py"""
import json, os, re
DIR = os.path.dirname(os.path.abspath(__file__))
TYPES = {"ninchi", "hozon", "kyokan", "hanten", "jisseki", "kyoiku"}
BAN = re.compile(r"http|lin\.ee|必ず治|100%|方へ|人へ|のです|しましょう|すべき")
SHINDAN_HINT = "固定投稿"


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
        if d.get("type") not in TYPES or hook in ex:
            skipped += 1; continue
        bad = [s for s in segs if BAN.search(s)]
        if bad or len(segs[0].replace("\n", "")) > 44:
            print("除外:", hook); skipped += 1; continue
        if is_yu:
            t = {"type": d["type"], "cat": "osaru", "disease": d.get("disease", "腰痛"), "segments": segs}
        else:
            t = {"type": d["type"], "cat": "osaru", "cta": "", "segments": segs}
            if d.get("cta") == "shindan" or SHINDAN_HINT in segs[-1]:
                t["shindan"] = True
        bank.append(t); ex.add(hook); n += 1
    json.dump(bank, open(bp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{bank_name}: 追加 {n} / 除外 {skipped} / 計 {len(bank)}")


def morning_priority():
    ap = os.path.join(DIR, "auto_post.py")
    s = open(ap, encoding="utf-8").read()
    pairs = [
        ('want_types = ("case2", "igai", "bui", "live", "rapport") if 5 <= hour < 12 else None',
         'want_types = ("case2", "ninchi", "hanten", "jisseki", "igai", "bui", "live", "rapport") if 5 <= hour < 12 else None'),
        ('want_types = ("yt", "bui", "dantei", "winning") if 6 <= hour < 10 else None',
         'want_types = ("ninchi", "hanten", "yt", "bui", "dantei", "winning") if 6 <= hour < 10 else None'),
    ]
    for old, new in pairs:
        if old in s:
            s = s.replace(old, new); print("朝優先枠を更新:", new[:60])
    open(ap, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    merge("draft_osaru_diet.json", "content_bank.json", False)
    merge("draft_osaru_yu.json", "content_bank_yu.json", True)
    morning_priority()
