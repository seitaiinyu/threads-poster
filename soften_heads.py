#!/usr/bin/env python3
"""見出しの断定が強い2本を弱める（医学的断定を避ける）。"""
import json, os
DIR = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(DIR, "content_bank_yu.json")
b = json.load(open(p, encoding="utf-8"))
REP = {
    "背筋運動で腰痛が悪化する理由": "背筋運動で腰痛が悪化することもある理由",
    "ストレッチで坐骨神経痛が悪化する理由": "ストレッチで坐骨神経痛が悪化することもある理由",
}
n = 0
for t in b:
    first = t["segments"][0].split("\n")[0]
    if first in REP:
        t["segments"][0] = t["segments"][0].replace(first, REP[first], 1); n += 1
json.dump(b, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("弱めた見出し:", n)
