#!/usr/bin/env python3
"""アカウント2（koshigaya_seitai_yu / 坐骨神経痛）のコンテンツバンク構築。
Obsidian「Threads投稿50本（坐骨神経痛）」＋手作りドラフトを、
地域ローカライズ＋来店CTA付きツリーに改良する。"""
import re, json, os, random

SRC = "/Users/takeuchiyuuki/Documents/Obsidian Vault/デスクトップ整理（2026年2〜3月）/SNS・Threads/Threads投稿50本（坐骨神経痛）.md"
random.seed(7)

# 近隣エリア（遠方の地域名をこれらに置換してローカル感を出す）
LOCAL = ["越谷市", "春日部市", "草加市", "さいたま市"]
FAR_CITIES = ["名古屋", "仙台", "大阪", "東京", "福岡", "札幌", "横浜", "京都", "神戸", "広島", "千葉", "川崎"]

# 来店CTA（坐骨・巡回）。プロフの公式LINE→キーワード「坐骨」
CTAS = [
    "越谷で坐骨神経痛を根本から見直したい方は、\nプロフの公式LINEから「坐骨」と送ってください。\nあなたの状態に合わせて返信します。",
    "「もう治らない」と諦める前に。\n越谷の整体院 優-YU- が、再発しない体づくりをサポートします。\nプロフの公式LINEから「坐骨」とメッセージください。",
    "自分の体のクセは自分では気づけません。\n越谷で坐骨神経痛を診てほしい方は、\nプロフの公式LINEから「坐骨」と送ってください。",
    "痛みを我慢し続ける前に、一度ご相談ください。\n越谷の整体院から、あなたに合った改善法をお伝えします。\nプロフの公式LINEから「坐骨」とメッセージを。",
]

# 手作りドラフト（A/B/C：越谷ローカル・高品質）
DRAFTS = [
    [
        "坐骨神経痛が\n何ヶ月も良くならないあなたへ。\n\n原因、座り方かもしれません。",
        "特に「内股の座り方」。\n女性に多いんですが、骨盤が内側にねじれて\nお尻の奥の筋肉（梨状筋）が神経を圧迫し続けます。\n\n痛みが取れないのは治療不足じゃなく、座り方が原因のことが多いです。",
        "やることはシンプル。\n・座骨を立てて座る\n・膝を軽く外に開く\n・15分に1回立つ\n\nこれだけで神経への圧迫がかなり変わります。",
    ],
    [
        "坐骨神経痛、\n「温めれば治る」と思ってる人、ちょっと待ってください。",
        "温めていいのは“慢性期”だけ。\nズキッと電気が走る急性期に温めると、炎症が広がって悪化することがあります。",
        "セルフチェックの目安はこちら👇\n・じっとしてもズキズキ →急性期（温めNG）\n・動き始めだけ痛い →慢性期（温めOK）",
    ],
]


def localize(text):
    for fc in FAR_CITIES:
        if fc in text:
            text = text.replace(fc, random.choice(LOCAL).replace("市", ""))
    return text


def split_segments(body):
    body = re.sub(r"\n-{3,}\s*$", "", body).strip()
    if "---SPLIT---" in body:
        segs = [s.strip() for s in body.split("---SPLIT---")]
    else:
        segs = [s.strip() for s in re.split(r"\n\s*\n", body)]
    return [s for s in segs if s]


def is_cta_like(seg):
    return any(k in seg for k in ["固定投稿", "http", "チェックして", "プロフ", "LINE"])


def parse_obsidian():
    text = open(SRC, encoding="utf-8").read()
    idx = text.find("## 全文一覧")
    body = text[idx:] if idx >= 0 else text
    blocks = re.split(r"\n###\s+No\.\d+[^\n]*\n", body)[1:]
    trees = []
    for b in blocks:
        segs = split_segments(b)
        # 末尾が既存CTA風なら除去（後で来店CTAを付ける）
        while segs and is_cta_like(segs[-1]):
            segs.pop()
        # ローカライズ
        segs = [localize(s) for s in segs]
        # 長すぎるセグメント(>480字)は除外対象としてスキップ判定
        segs = [s for s in segs if len(s) <= 480]
        if len(segs) >= 2:
            trees.append(segs)
    return trees


def main():
    bank = []
    ci = 0
    for segs in DRAFTS:
        s = list(segs) + [CTAS[ci % len(CTAS)]]; ci += 1
        bank.append({"type": "draft", "segments": s})
    for segs in parse_obsidian():
        s = list(segs) + [CTAS[ci % len(CTAS)]]; ci += 1
        bank.append({"type": "tip", "segments": s})
    json.dump(bank, open("content_bank_yu.json", "w"), ensure_ascii=False, indent=1)
    print(f"アカウント2バンク作成: {len(bank)}ツリー（draft {sum(1 for x in bank if x['type']=='draft')} / tip {sum(1 for x in bank if x['type']=='tip')}）")
    print("\n--- サンプル(3本目) ---")
    for i, s in enumerate(bank[2]["segments"], 1):
        print(f"[{i}] {s[:45].replace(chr(10),' ')}...")


if __name__ == "__main__":
    main()
