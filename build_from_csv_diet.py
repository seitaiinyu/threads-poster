#!/usr/bin/env python3
"""アカウント1(回復中)のCSVから、違反・宣伝・体重数値訴求を全除外した純教育ツリーを抽出。
3部構成化・年齢40〜50代・近隣ローカライズ・安全CTA(回復期は非投稿)・スマホ整形。"""
import csv, json, os, re, random

DIR = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.expanduser("~/Desktop/ダイエットver2.1 - 自由投稿管理（順番なし）.csv")
random.seed(13)
MAX_ADD = 40

# 厳格除外（違反＋宣伝＋外部誘導＋約束）
NG = ["lin.ee", "http", "公式LINE", "最後のダイエット", "人生最後", "フォローして", "友だち追加",
      "予約", "当院", "整体院", "新越谷", "遺伝子検査", "問い合わせ", "施術", "プロフ", "DM",
      "ライン", "LINE", "限定", "名様", "キャンペーン", "クーポン", "割引", "@koshigaya",
      "円", "保証", "必ず痩せ", "絶対痩せ", "100%"]
TOPIC = ["ダイエット", "痩せ", "脂肪", "食事", "糖質", "タンパク質", "代謝", "カロリー", "血糖値",
         "筋肉", "睡眠", "体重", "むくみ", "食べ", "太る", "空腹", "間食", "運動", "ホルモン", "腸"]
NEAR = ["越谷", "草加", "吉川", "さいたま", "松伏", "川口", "春日部"]
FAR = ["名古屋","仙台","大阪","東京","福岡","札幌","横浜","京都","神戸","広島","千葉","川崎",
       "岡山","鹿児島","静岡","新潟","松山","盛岡","宇都宮","宮崎","長野","岐阜","熊本"]
CTAS = [
    "越谷でダイエットに取り組む方へ。\n無理なく続ける食事のコツを発信しています。\nよかったらプロフィールものぞいてみてください。",
    "整体院 優-YU-（越谷）では、\n体質に合わせたダイエットのご相談を受けています。\n詳しくはプロフィールをご覧ください。",
    "一人で続けるのが難しいと感じたら。\n越谷で一緒に取り組めます。\n気になる方はプロフィールをチェックしてみてください。",
    "越谷で健康的に体を変えていきたい方へ。\n具体的な進め方はプロフィールからご確認いただけます。",
]
KG = re.compile(r"\d+\s*(kg|㎏|キロ|キョ)")


def clean(t):
    return t and not any(w in t for w in NG) and not KG.search(t)


def relevant(segs):
    body = "".join(segs)
    return sum(1 for k in TOPIC if k in body) >= 2


def localize(t):
    for fc in FAR:
        if fc in t:
            t = t.replace(fc, random.choice(NEAR))
    return t


def rand_age(t):
    return re.sub(r"\d{1,3}歳", f"{random.randint(40,59)}歳", t)


def to_3part(segs):
    if len(segs) <= 3:
        return segs
    hook = segs[0]
    lists = [i for i in range(1, len(segs)) if "・" in segs[i]]
    si = lists[-1] if lists else len(segs) - 1
    mids = [segs[i] for i in range(1, si)]
    edu = max(mids, key=len) if mids else segs[1]
    return [hook, edu, segs[si]]


def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    children = {}
    for r in rows:
        rep = r.get("返信先ID", "").strip()
        if rep:
            children.setdefault(rep, []).append(r)
    roots = [r for r in rows if not r.get("返信先ID", "").strip() and r.get("本文", "").strip()]

    def build(root):
        segs = [root["本文"].strip()]
        cur = root.get("投稿ID", "").strip()
        d = 0
        while cur in children and d < 6:
            nxt = children[cur][0]
            segs.append(nxt["本文"].strip())
            cur = nxt.get("投稿ID", "").strip()
            d += 1
        return segs

    bankp = os.path.join(DIR, "content_bank.json")
    bank = json.load(open(bankp, encoding="utf-8"))
    existing = {t["segments"][0].split("\n")[0].strip() for t in bank}

    added = ci = 0
    for root in roots:
        if added >= MAX_ADD:
            break
        segs = build(root)
        if not (2 <= len(segs) <= 5):
            continue
        if any(not clean(s) for s in segs):
            continue
        if any(len(s) < 8 or len(s) > 400 for s in segs):
            continue
        if len(segs[0]) < 14 or not relevant(segs):
            continue
        hook = segs[0].split("\n")[0].strip()
        if hook in existing:
            continue
        segs = [localize(rand_age(s)) for s in segs]
        three = to_3part(segs)
        existing.add(hook)
        bank.append({"type": "library", "segments": three, "cta": CTAS[ci % len(CTAS)]})
        ci += 1
        added += 1
    json.dump(bank, open(bankp, "w"), ensure_ascii=False, indent=1)
    print(f"アカウント1: CSVから純教育ツリー {added}本追加 / バンク計 {len(bank)}")


if __name__ == "__main__":
    main()
