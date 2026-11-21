#!/usr/bin/env python3
"""draft_yt_yu3.json（本人のYouTube動画9本由来・続きを読ませる4段ツリー）をA2バンクへ追加。
type=yt は朝の優先枠(bui/dantei/winning)に加える。"""
import json, os, re
DIR = os.path.dirname(os.path.abspath(__file__))
BAN = re.compile(r"太ももが痩せにくい|しましょう|すべき|ではありません|存在しません|http|lin\.ee|必ず治|100%|方へ")


def main():
    draft = json.load(open(os.path.join(DIR, "draft_yt_yu3.json"), encoding="utf-8"))
    p = os.path.join(DIR, "content_bank_yu.json")
    bank = json.load(open(p, encoding="utf-8"))
    ex = {t["segments"][0].split("\n")[0].strip() for t in bank}
    n = line = skipped = 0
    for d in draft:
        segs = [s.strip() for s in d["segments"]]
        hook = segs[0].split("\n")[0].strip()
        if hook in ex:
            skipped += 1; continue
        if any(BAN.search(s) for s in segs):
            print("禁止語で除外:", hook); skipped += 1; continue
        t = {"type": "yt", "cat": d.get("cat", "education"), "disease": d["disease"], "segments": segs}
        if d.get("cta") == "line":
            line += 1
        bank.append(t); n += 1
    json.dump(bank, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"追加 {n}本（LINE誘導 {line}本）/ 除外 {skipped} / バンク計 {len(bank)}")

    # 朝の優先型に yt を追加
    ap = os.path.join(DIR, "auto_post.py")
    s = open(ap, encoding="utf-8").read()
    old = 'want_types = ("bui", "dantei", "winning") if 6 <= hour < 10 else None'
    if old in s:
        s = s.replace(old, 'want_types = ("yt", "bui", "dantei", "winning") if 6 <= hour < 10 else None')
        open(ap, "w", encoding="utf-8").write(s)
        print("A2 朝優先枠に yt を追加")


if __name__ == "__main__":
    main()
