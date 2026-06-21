#!/usr/bin/env python3
"""バンクの各ツリーを5つの型に分類して cat フィールドを付与。
型: empathy(共感) / education(教育) / case(事例) / personality(人柄) / funnel(動線)"""
import json, os, sys, re
from collections import Counter

DIR = os.path.dirname(os.path.abspath(__file__))

EMP = ["あなたへ", "ませんか", "悩", "つらい", "辛い", "諦め", "困っ", "苦しい", "不安",
       "気にしてる", "気にして", "やめられない", "止まらない", "怖い", "心配"]
EDU = ["＝", "なぜ", "理由", "仕組み", "メカニズム", "原因", "研究", "報告", "実は",
       "ホルモン", "血糖", "代謝", "筋肉", "神経", "骨盤", "5選", "3選", "特徴", "方法"]
PERS = ["僕は", "私は", "正直に言う", "告白", "恥ずかしながら", "今日は", "実は僕",
        "個人的に", "経験者の僕"]
FUNNEL = ["プロフィール", "公式LINE", "ご相談", "カウンセリング", "ご予約", "お越しください"]
CASE = ["在住", "歳の女性", "歳の男性", "【", "お客様", "ビフォー"]


def categorize(tree):
    segs = tree["segments"]
    body = "".join(segs)
    hook = segs[0]
    t = tree.get("type", "")
    # 明示的に作成した型は尊重
    if t in ("personality", "funnel"):
        return t
    if t == "case" or any(k in body for k in CASE):
        return "case"
    # CTAが本文の主役（動線）
    if (len(segs) <= 2 and any(k in body for k in FUNNEL)):
        return "funnel"
    if any(k in hook for k in PERS):
        return "personality"
    if any(k in hook for k in EMP):
        return "empathy"
    if any(k in body for k in EDU):
        return "education"
    return "education"


def main():
    apply = "--apply" in sys.argv
    for fn in ["content_bank.json", "content_bank_yu.json"]:
        p = os.path.join(DIR, fn)
        bank = json.load(open(p, encoding="utf-8"))
        cats = Counter()
        for t in bank:
            c = categorize(t)
            cats[c] += 1
            if apply:
                t["cat"] = c
        if apply:
            json.dump(bank, open(p, "w"), ensure_ascii=False, indent=1)
        label = "アカウント1" if "yu" not in fn else "アカウント2"
        print(f"{label}: {dict(cats)} 計{len(bank)}")


if __name__ == "__main__":
    main()
