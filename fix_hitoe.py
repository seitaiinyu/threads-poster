#!/usr/bin/env python3
"""「〜の人へ」「〜な人へ」などの呼びかけを「〜のあなたへ」に統一する（両バンク）。
「人へ」が行末・句読点前に来るものだけ対象。「人は」「人が」等は変えない。"""
import json, os, re
DIR = os.path.dirname(os.path.abspath(__file__))
PAT = re.compile(r"人へ(?=[。、！!\n]|$)")

for fn in ("content_bank.json", "content_bank_yu.json"):
    p = os.path.join(DIR, fn)
    b = json.load(open(p, encoding="utf-8"))
    n = 0
    for t in b:
        for i, s in enumerate(t["segments"]):
            s2 = PAT.sub("あなたへ", s)
            if s2 != s:
                t["segments"][i] = s2; n += 1
    json.dump(b, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    left = sum(1 for t in b for s in t["segments"] if PAT.search(s))
    print(f"{fn}: 修正{n}箇所 / 残り{left}")
