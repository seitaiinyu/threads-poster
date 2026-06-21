#!/usr/bin/env python3
"""不足している『人柄(personality)』『動線(funnel)』の型をバンクに追加。安全・規約準拠。"""
import json, os
DIR = os.path.dirname(os.path.abspath(__file__))

# ---- アカウント1（ダイエット）----
DIET_PERSONALITY = [
    ["正直に言うと、\n僕も昔は食事制限が全然続かないタイプでした。",
     "意志が弱いと自分を責めていましたが、\n続かないのは「やり方」のせいだと気づいてから変わりました。",
     "だから今は、無理なく続けられる方法を\n一番大事にしてお伝えしています。"],
    ["今日は少しだけ僕の話を。",
     "ダイエットのサポートを始めたのは、\n「頑張っているのに報われない」方を\n何人も見てきたからです。",
     "頑張りを結果に変えるお手伝いがしたい。\nそんな想いで毎日発信しています。"],
    ["お客様によく言われるんです。\n「もっと早く知りたかった」って。",
     "それくらい、世の中には\n遠回りなダイエット情報があふれています。",
     "だから僕は、本質的で続けられることだけを\nお伝えするようにしています。"],
]
DIET_FUNNEL = [
    ["ダイエットを基礎から見直したい方へ。",
     "無理な食事制限ではなく、\n体質に合わせた進め方をお伝えしています。",
     "気になる方は、プロフィールをのぞいてみてください。"],
    ["一人で頑張るのが難しいと感じたら。",
     "越谷の整体院 優-YU- が、\nあなたのペースに合わせてサポートします。",
     "詳しくはプロフィールからご確認いただけます。"],
]

# ---- アカウント2（坐骨）----
YU_PERSONALITY = [
    ["実は僕自身も、\n坐骨神経痛で悩んだ時期があります。",
     "あの痛みのつらさ、\n夜眠れない不安は痛いほどわかります。",
     "だからこそ、同じように悩む方の力になりたくて\n毎日発信しています。"],
    ["この仕事をしていて\n一番うれしい瞬間があります。",
     "「また旅行に行けました」\n「孫を抱っこできました」\nそんな声を聞けた時です。",
     "痛みのない毎日を取り戻すお手伝いがしたい。\nそれが僕の原点です。"],
    ["正直に言いますね。",
     "坐骨神経痛は、原因を見極めれば\n多くの方が良くなります。\nでも自己流だと遠回りになりがちです。",
     "だから僕は、正しい順番を\nわかりやすく伝えることを大切にしています。"],
]
YU_FUNNEL = [
    ["坐骨神経痛を根本から見直したい方へ。",
     "体の状態に合わせたケアをご提案しています。\n自己流で悪化させる前に。",
     "気になる方は、プロフィールをのぞいてみてください。"],
    ["痛みを我慢し続けていませんか。",
     "越谷の整体院 優-YU- が、\n再発しにくい体づくりをサポートします。",
     "詳しくはプロフィールからご確認いただけます。"],
]


def add(fn, pers, funnel):
    p = os.path.join(DIR, fn)
    bank = json.load(open(p, encoding="utf-8"))
    existing = {t["segments"][0].split("\n")[0].strip() for t in bank}
    n = 0
    for segs in pers:
        if segs[0].split("\n")[0] in existing:
            continue
        bank.append({"type": "personality", "cat": "personality", "segments": segs}); n += 1
    for segs in funnel:
        if segs[0].split("\n")[0] in existing:
            continue
        bank.append({"type": "funnel", "cat": "funnel", "segments": segs}); n += 1
    json.dump(bank, open(p, "w"), ensure_ascii=False, indent=1)
    print(f"{fn}: 人柄・動線 {n}本追加 / 計{len(bank)}")


if __name__ == "__main__":
    add("content_bank.json", DIET_PERSONALITY, DIET_FUNNEL)
    add("content_bank_yu.json", YU_PERSONALITY, YU_FUNNEL)
