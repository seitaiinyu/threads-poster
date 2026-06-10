#!/usr/bin/env python3
"""アカウント2バンクのCTA(最終段)を規約安全な文言に差し替え（多様化・保証なし・プロフィール誘導）。"""
import json, os
DIR = os.path.dirname(os.path.abspath(__file__))

SAFE_CTAS = [
    "越谷で坐骨神経痛にお悩みの方へ。\n体の状態に合わせたケアをご提案しています。\nよかったらプロフィールものぞいてみてください。",
    "整体院 優-YU-（越谷）では、\n坐骨神経痛のご相談を受けています。\n詳しくはプロフィールをご覧ください。",
    "痛みを一人で我慢していませんか。\n越谷で根本からのケアに取り組めます。\n気になる方はプロフィールをチェックしてみてください。",
    "越谷で坐骨神経痛を見直したい方へ。\n進め方はプロフィールからご確認いただけます。",
    "自分の体のクセは気づきにくいもの。\n越谷の整体院 優-YU- がサポートします。\nプロフィールからお気軽にどうぞ。",
]

def main():
    p = os.path.join(DIR, "content_bank_yu.json")
    bank = json.load(open(p, encoding="utf-8"))
    ci = fixed = 0
    for t in bank:
        segs = t["segments"]
        if len(segs) >= 2:
            segs[-1] = SAFE_CTAS[ci % len(SAFE_CTAS)]
            ci += 1; fixed += 1
    json.dump(bank, open(p, "w"), ensure_ascii=False, indent=1)
    print(f"アカウント2 CTA刷新: {fixed}本")

if __name__ == "__main__":
    main()
