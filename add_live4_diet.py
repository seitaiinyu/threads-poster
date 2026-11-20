#!/usr/bin/env python3
"""draft_live4.json（LIVE 10/18〜11/15 由来・続きを読ませる3段ツリー）をA1バンクへ追加。
shindan=true の投稿は固定投稿の診断へ誘導する一文入り（火金日の1本目に優先配信）。"""
import json, os, re
DIR = os.path.dirname(os.path.abspath(__file__))
BAN = re.compile(r"しましょう|すべき|ではありません|存在しません|摂取|実践|http|lin\.ee|お盆|必ず痩せ")


def main():
    draft = json.load(open(os.path.join(DIR, "draft_live4.json"), encoding="utf-8"))
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
        t = {"type": "live", "cat": d.get("cat", "education"), "cta": "", "segments": segs}
        if d.get("shindan"):
            t["shindan"] = True; sh += 1
        bank.append(t); n += 1
    json.dump(bank, open(p, "w"), ensure_ascii=False, indent=1)
    print(f"追加 {n}本（診断誘導 {sh}本）/ 除外 {skipped} / バンク計 {len(bank)}")


if __name__ == "__main__":
    main()
