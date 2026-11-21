#!/usr/bin/env python3
"""A1の事例型(case2)16本に、Instagramの1枚目画像(images/<id>.jpg)を紐づける。
あわせて、診断誘導なしの事例には「カウンセリング＋痩身整体のご予約→LINE」の締めを付ける。
対応は draft_cases_diet.json の並び順（執筆役の事例番号）に基づく。"""
import json, os
DIR = os.path.dirname(os.path.abspath(__file__))
IDS = [
    "Df4Z9c6EwqT",  # 1 更年期・健診 −7kg
    "Dfrf0rxE9k7",  # 2 健診が憂鬱 −8.1kg
    "Dfjxm8vE6lm",  # 3 写真に写りたくない
    "DbW_5LGkwO0",  # 4 リバウンド −14.2kg
    "DcnmeC8ETCO",  # 5 旅行 −10.4kg
    "DbXAQd7k9c5",  # 6 血圧・お酒 −7.3kg
    "Dep0PZYE0B4",  # 7 80kg超 −5kg
    "DbAQn1HEV73",  # 8 何をやっても −10.9kg
    "DbXBVFVk5bM",  # 9 ヨガ・パーソナル −13.8kg
    "DbXAEAGk0Ws",  # 10 運動なし −7.3kg
    "De9IiNyE-Ee",  # 11 子どもと遊べない母 −6.2kg
    "De3JBStE_Xb",  # 12 男性 −6.2kg
    "DZqyYVIEz9Q",  # 13 髪・肌 −9.4kg
    "Dc0hAPJk0lT",  # 14 食べるのが好き −7.1kg
    "DZtG0rCE9B8",  # 15 事例4の別切り口 −14.2kg
    "DfE30PgEy17",  # 16 事例11の別切り口 −6.2kg
]
LINE_CTA = "カウンセリング＋痩身整体のご予約は、\nプロフィールのリンクからLINEでどうぞ。"

p = os.path.join(DIR, "content_bank.json")
bank = json.load(open(p, encoding="utf-8"))
cases = [t for t in bank if t.get("type") == "case2"]
assert len(cases) == len(IDS), f"事例数{len(cases)}とID数{len(IDS)}が不一致"
img_ok = 0; line_ok = 0
for t, vid in zip(cases, IDS):
    f = f"{vid}.jpg"
    if os.path.exists(os.path.join(DIR, "images", f)):
        t["image"] = f; img_ok += 1
    else:
        t.pop("image", None)
    if not t.get("shindan") and LINE_CTA not in t["segments"][-1]:
        t["segments"][-1] = t["segments"][-1].rstrip() + "\n\n" + LINE_CTA
        line_ok += 1
json.dump(bank, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"画像を紐づけ: {img_ok}/{len(IDS)} / LINE予約の締めを追加: {line_ok}本")
