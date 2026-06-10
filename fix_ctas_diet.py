#!/usr/bin/env python3
"""アカウント1バンクのCTA(最終段)を、規約安全な文言に差し替える（多様化・保証表現/最後のダイエット/直リンク除去）。"""
import json, os
DIR = os.path.dirname(os.path.abspath(__file__))

# 規約安全CTA：断定/保証なし・「最後のダイエット」なし・直リンクなし・プロフィール誘導・文言を多様化
SAFE_CTAS = [
    "越谷でダイエットに取り組む方へ。\n無理なく続ける食事のコツを発信しています。\nよかったらプロフィールものぞいてみてください。",
    "整体院 優-YU-（越谷）では、\n体質に合わせたダイエットのご相談を受けています。\n詳しくはプロフィールをご覧ください。",
    "一人で続けるのが難しいと感じたら。\n越谷で一緒に取り組めます。\n気になる方はプロフィールをチェックしてみてください。",
    "越谷で健康的に体を変えていきたい方へ。\n具体的な進め方はプロフィールからご確認いただけます。",
    "ダイエットの悩み、一人で抱えていませんか。\n越谷の整体院 優-YU- がサポートします。\nプロフィールからお気軽にどうぞ。",
]

def main():
    p = os.path.join(DIR, "content_bank.json")
    bank = json.load(open(p, encoding="utf-8"))
    ci = 0
    fixed = 0
    for t in bank:
        segs = t["segments"]
        if len(segs) >= 2:
            segs[-1] = SAFE_CTAS[ci % len(SAFE_CTAS)]
            ci += 1
            fixed += 1
    json.dump(bank, open(p, "w"), ensure_ascii=False, indent=1)
    print(f"CTA刷新: {fixed}本のCTAを安全文言に差し替え")

if __name__ == "__main__":
    main()
