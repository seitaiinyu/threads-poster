#!/usr/bin/env python3
"""アカウント1: 痩せない原因タイプ診断への誘導投稿。
本文にリンクは貼らず『固定投稿から診断できます』へ誘導。参加型フック。
shindan=True を付け、週2〜3本の低頻度で配信する。"""
import json, os
DIR = os.path.dirname(os.path.abspath(__file__))

# 診断誘導のまとめ文（巡回）。リンクは貼らない。
GUIDES = [
    "5問・30秒で分かる無料診断を作りました。\n「痩せない本当の原因」、\n固定投稿から診断できます。",
    "あなたのタイプは、\nプロフィールの固定投稿から\n30秒で診断できます。無料です。",
    "原因が分かれば、対策が変わります。\nまずは固定投稿の無料診断で\n自分のタイプを確かめてみてください。",
]

# (フック, 教育) ※③はGUIDESを巡回
ITEMS = [
    ["痩せない原因、実は人によって違います。\nあなたはどのタイプ？",
        "・食べてないのに太る人\n・夜に食べすぎる人\n・むくみやすい人\n原因が違えば、正解のダイエットも変わります。"],
    ["同じ食事制限でも、\n痩せる人と痩せない人がいます。\nその差は「タイプ」かもしれません。",
        "人によって、\n糖質で太りやすい・脂質で太りやすい・\nむくみで太りやすい、と体質が違います。\n自分のタイプを知ることが第一歩です。"],
    ["「何をやっても痩せない」あなたへ。\nやり方ではなく“タイプ”が合っていないだけかも。",
        "世の中のダイエット法は\n特定のタイプにしか効かないものが多いです。\nだから、まず自分の原因タイプを知るのが近道です。"],
    ["あなたが太りやすい食べ物、\n実は人それぞれ違うのを知っていますか？",
        "ある人はご飯やパン、\nある人は脂っこいもの、\nある人は塩分でむくむ。\n原因を外すと、いくら頑張っても痩せません。"],
    ["ダイエットを始める前に、\nまず知ってほしいことがあります。",
        "それは「自分がなぜ太るのか」。\n原因は大きく分けて数タイプ。\nそこを間違えると遠回りになります。"],
    ["痩せない本当の原因、\n5問で分かるとしたら気になりませんか？",
        "・つい食べすぎる\n・水太り／むくみ\n・代謝の低下\nあなたの原因タイプによって、\n今日からやるべきことが変わります。"],
]


def main():
    p = os.path.join(DIR, "content_bank.json")
    bank = json.load(open(p, encoding="utf-8"))
    # 既存のshindanを除去（再実行時のため）
    bank = [t for t in bank if not t.get("shindan")]
    existing = {t["segments"][0].split("\n")[0].strip() for t in bank}
    n = 0
    for i, (hook, edu) in enumerate(ITEMS):
        if hook.split("\n")[0].strip() in existing:
            continue
        bank.append({"type": "shindan", "cat": "participation", "shindan": True,
                     "segments": [hook, edu, GUIDES[i % len(GUIDES)]]})
        n += 1
    json.dump(bank, open(p, "w"), ensure_ascii=False, indent=1)
    print(f"診断誘導投稿 {n}本追加 / バンク計 {len(bank)}")


if __name__ == "__main__":
    main()
