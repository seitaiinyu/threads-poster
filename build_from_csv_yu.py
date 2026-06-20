#!/usr/bin/env python3
"""アカウント2のCSV投稿ライブラリから、違反・宣伝を除いた純粋な教育ツリーを抽出してバンク追加。
返信先IDでツリーを復元 → 厳格フィルタ → 近隣ローカライズ → 安全CTA付与 → 既存と重複排除。"""
import csv, json, os, re, random

DIR = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.expanduser("~/Desktop/整体用Threads - 自由投稿管理（順番なし）.csv")
random.seed(11)
MAX_ADD = 45

# 除外フレーズ（違反＋宣伝＋外部誘導＋実績数値訴求）
NG = ["lin.ee", "http", "公式LINE", "スレッズ」とコメント", "コメントしてね", "フォローして",
      "最後の", "友だち追加", "予約", "当院", "整体院", "新越谷", "お問い合わせ", "問い合わせ",
      "施術", "円", "プロフ", "DM", "ライン", "LINE", "限定", "名様", "キャンペーン",
      "クーポン", "割引", "@koshigaya"]
NEAR = ["越谷", "草加", "吉川", "さいたま", "松伏", "川口", "春日部"]
FAR = ["名古屋","仙台","大阪","東京","福岡","札幌","横浜","京都","神戸","広島","千葉","川崎",
       "岡山","鹿児島","静岡","新潟","松山","盛岡","宇都宮","宮崎","長野","岐阜","熊本","旭川",
       "長崎","青森","秋田","金沢","和歌山","高松","徳島","松本","浜松","堺"]

CTAS = [
    "越谷で坐骨神経痛にお悩みの方へ。\n体の状態に合わせたケアをご提案しています。\nよかったらプロフィールものぞいてみてください。",
    "整体院 優-YU-（越谷）では、\n坐骨神経痛のご相談を受けています。\n詳しくはプロフィールをご覧ください。",
    "痛みを一人で我慢していませんか。\n越谷で根本からのケアに取り組めます。\n気になる方はプロフィールをチェックしてみてください。",
    "自分の体のクセは気づきにくいもの。\n越谷の整体院 優-YU- がサポートします。\nプロフィールからお気軽にどうぞ。",
]


def clean(text):
    return text and not any(w in text for w in NG)


def localize(t):
    for fc in FAR:
        if fc in t:
            t = t.replace(fc, random.choice(NEAR))
    return t


def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    by_id = {}
    children = {}
    for r in rows:
        pid = r.get("投稿ID", "").strip()
        if pid:
            by_id[pid] = r
        rep = r.get("返信先ID", "").strip()
        if rep:
            children.setdefault(rep, []).append(r)

    # ルート = 返信先IDなし & 本文あり
    roots = [r for r in rows if not r.get("返信先ID", "").strip() and r.get("本文", "").strip()]

    def build_tree(root):
        segs = [root["本文"].strip()]
        cur = root.get("投稿ID", "").strip()
        depth = 0
        while cur in children and depth < 6:
            nxt = children[cur][0]
            segs.append(nxt["本文"].strip())
            cur = nxt.get("投稿ID", "").strip()
            depth += 1
        return segs

    existing = set()
    bankp = os.path.join(DIR, "content_bank_yu.json")
    bank = json.load(open(bankp, encoding="utf-8"))
    for t in bank:
        existing.add(t["segments"][0].split("\n")[0].strip())

    added = 0
    ci = 0
    for root in roots:
        if added >= MAX_ADD:
            break
        segs = build_tree(root)
        # 全コマがクリーン、2〜4コマ、各コマ妥当な長さ
        if not (2 <= len(segs) <= 4):
            continue
        if any(not clean(s) for s in segs):
            continue
        if any(len(s) < 8 or len(s) > 400 for s in segs):
            continue
        hook = segs[0].split("\n")[0].strip()
        if hook in existing:
            continue
        segs = [localize(s) for s in segs]
        existing.add(hook)
        bank.append({"type": "library", "segments": segs + [CTAS[ci % len(CTAS)]]})
        ci += 1
        added += 1

    json.dump(bank, open(bankp, "w"), ensure_ascii=False, indent=1)
    print(f"CSVライブラリから追加: {added}ツリー / バンク計 {len(bank)}")


if __name__ == "__main__":
    main()
