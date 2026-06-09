#!/usr/bin/env python3
"""Obsidianのダイエット50本＋事例型を、来店CTA付きツリーに改良してcontent_bank.jsonを作る。"""
import re, json, os

SRC = "/Users/takeuchiyuuki/Documents/Obsidian Vault/デスクトップ整理（2026年2〜3月）/SNS・Threads/Threads投稿50本（ダイエット）.md"

# 来店促進CTA（巡回）。プロフの公式LINE→キーワード「ダイエット」
CTAS = [
    "越谷で“最後のダイエット”にしたい方へ。\n運動も食事制限もなしで結果を出す方法を、\nプロフの公式LINEから「ダイエット」と送ってくれた方にお伝えしています。",
    "「何をやっても痩せなかった」あなたへ。\n越谷のダイエット整体院 優-YU- が、\n体質から変えるお手伝いをします。\nプロフの公式LINEから「ダイエット」とメッセージを。",
    "一人で頑張るのに疲れたら、\n越谷で一緒に変えていきましょう。\nプロフの公式LINEから「ダイエット」と送ると、\n初回カウンセリングのご案内をします。",
    "越谷でリバウンドしない体を手に入れたい方は、\nプロフの公式LINEから「ダイエット」とメッセージください。\nあなたに合った進め方をご提案します。",
]

# 実績の高い事例型（最強コンバート）。近隣4エリア（越谷・春日部・草加・さいたま）で展開
CASE_TREES = [
    [
        "【越谷市】\n62歳の女性が2ヶ月で5.2kg落ちました。\n\n運動はなし。\nやめたこと、たった2つだけです。",
        "この方は「もう歳だから痩せない」と諦めていました。\n\nでも原因は年齢ではなく“夜の食べ方”。\n夜に糖質をとる→インスリンが出る→脂肪に直行。",
        "やめたのはこの2つ。\n①夜の炭水化物を抜く\n②食べる時間を8時間以内に区切る\n\n胃腸が休まると、体は脂肪を燃やし始めます。",
    ],
    [
        "【春日部市】\n58歳の女性が、ジムにも通わず\n3ヶ月で6kg落としました。\n\nやったことは“朝の習慣”を変えただけ。",
        "朝起きてすぐ食べると、\n血糖値が乱れて1日中脂肪を溜め込みやすくなります。\n\nこの方は朝の順番を変えただけでした。",
        "・起きてコップ1杯の水\n・タンパク質から食べる\n・甘い飲み物をやめる\n\nたったこれだけで体は変わり始めます。",
    ],
    [
        "【草加市】\n45歳の女性が、産後ずっと落ちなかった体重を\n2ヶ月で4.8kg落としました。\n\nきっかけは“ある勘違い”に気づいたこと。",
        "「カロリーを減らせば痩せる」と\nサラダだけの生活をしていたこの方。\n\n実は、極端な食事制限が代謝を落とし、\n逆に痩せにくい体を作っていました。",
        "やったのは“しっかり食べる”こと。\n・3食タンパク質を入れる\n・夜だけ炭水化物を控える\n・水を1.5L飲む\n\n食べて痩せる、が正解でした。",
    ],
    [
        "【さいたま市】\n51歳の女性が、更年期で増えた体重を\n3ヶ月で5.5kg落としました。\n\n激しい運動は一切していません。",
        "更年期はホルモンの変化で\n脂肪が燃えにくくなる時期。\n\n“頑張る”より“整える”方向に切り替えたのが\nこの方の正解でした。",
        "・夜のタンパク質を増やす\n・睡眠を6時間以上とる\n・朝に軽く歩く\n\n体が整うと、自然と落ち始めます。",
    ],
]


def parse_obsidian():
    text = open(SRC, encoding="utf-8").read()
    # 全文一覧以降
    idx = text.find("## 全文一覧")
    body = text[idx:]
    # 「### No.X ...」で分割
    blocks = re.split(r"\n###\s+No\.\d+[^\n]*\n", body)[1:]
    trees = []
    for b in blocks:
        b = b.strip()
        # 末尾の区切り「---」を除去
        b = re.sub(r"\n-{3,}\s*$", "", b).strip()
        segs = [s.strip() for s in b.split("---SPLIT---")]
        segs = [s for s in segs if s]
        if len(segs) >= 2:
            trees.append(segs)
    return trees


def main():
    obs = parse_obsidian()
    bank = []
    ci = 0
    # 事例型を先頭に
    for t in CASE_TREES:
        segs = [s for s in t if s is not None]
        segs.append(CTAS[ci % len(CTAS)]); ci += 1
        bank.append({"type": "case", "segments": segs})
    # Obsidian50本
    for segs in obs:
        segs = list(segs)
        segs.append(CTAS[ci % len(CTAS)]); ci += 1
        bank.append({"type": "tip", "segments": segs})
    json.dump(bank, open("content_bank.json", "w"), ensure_ascii=False, indent=1)
    print(f"コンテンツバンク作成: {len(bank)}ツリー")
    print(f"  事例型: {sum(1 for x in bank if x['type']=='case')} / Tips型: {sum(1 for x in bank if x['type']=='tip')}")
    # サンプル表示
    print("\n--- サンプル(1本目) ---")
    for i, s in enumerate(bank[0]["segments"], 1):
        print(f"[{i}] {s[:50].replace(chr(10),' ')}...")


if __name__ == "__main__":
    main()
