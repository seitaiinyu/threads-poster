#!/usr/bin/env python3
"""draft_cases_diet.json（Instagramのお客様事例由来・事例型3段ツリー）をA1バンクへ追加。
type=case2 を朝の優先枠に加える。"""
import json, os, re
DIR = os.path.dirname(os.path.abspath(__file__))
BAN = re.compile(r"しましょう|すべき|ではありません|存在しません|http|lin\.ee|必ず|100%|方へ|人へ|のです|ことが多いです|可能性があります")


def main():
    draft = json.load(open(os.path.join(DIR, "draft_cases_diet.json"), encoding="utf-8"))
    p = os.path.join(DIR, "content_bank.json")
    bank = json.load(open(p, encoding="utf-8"))
    ex = {t["segments"][0].split("\n")[0].strip() for t in bank}
    n = sh = skipped = 0
    for d in draft:
        segs = [s.strip() for s in d["segments"]]
        hook = segs[0].split("\n")[0].strip()
        if hook in ex:
            skipped += 1; continue
        if any(BAN.search(s) for s in segs):
            print("禁止語で除外:", hook); skipped += 1; continue
        t = {"type": "case2", "cat": "case", "cta": "", "segments": segs}
        if d.get("shindan"):
            t["shindan"] = True; sh += 1
        bank.append(t); n += 1
    json.dump(bank, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"追加 {n}本（診断誘導 {sh}本）/ 除外 {skipped} / バンク計 {len(bank)}")

    ap = os.path.join(DIR, "auto_post.py")
    s = open(ap, encoding="utf-8").read()
    old = 'want_types = ("igai", "bui", "live", "rapport") if 5 <= hour < 12 else None'
    if old in s:
        s = s.replace(old, 'want_types = ("case2", "igai", "bui", "live", "rapport") if 5 <= hour < 12 else None')
        open(ap, "w", encoding="utf-8").write(s)
        print("A1 朝優先枠に case2 を追加")


if __name__ == "__main__":
    main()
