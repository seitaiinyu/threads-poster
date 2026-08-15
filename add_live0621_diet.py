#!/usr/bin/env python3
"""6/21 LIVE(結果が出ない人の特徴3つ)をA1の投稿に変換。
既存のlive投稿(6/6由来)と重複しない切り口のみ: 知識より行動/継続できる方法か/
食事と遺伝子が中心/コンフォートゾーン。"""
import json, os
DIR = os.path.dirname(os.path.abspath(__file__))
T = [
 ("personality",["知識に、価値はありません。\n少し厳しいですが、本気でそう思っています。",
   "ダイエットの情報はあふれています。\n知っているだけでは何も変わりません。\n価値があるのは「行動」です。\n知識を使い、行動し、結果を見て、\nまた行動を変える。",
   "このサイクルを回した人だけが\n変わっていきます。\n今日、1つだけ行動に移してみませんか。"]),
 ("education",["そのダイエット、\nサポート期間が終わった後も\n自分で続けられますか。",
   "マシンを当てるだけ、打つだけ、飲むだけ。\nその期間は効果があっても、\n終わったら自分では続けられません。\nだから戻りやすいのです。",
   "選ぶ基準はシンプルです。\n「自分の力で継続できる方法か」。\nそこを見極めてください。"]),
 ("education",["あなたの人生で「これからも続くもの」と\n「変わらないもの」は何だと思いますか。",
   "続くものは、食事。\n変わらないものは、生まれ持った体質です。\nこの2つを無視したダイエットは\nリバウンドしやすくなります。",
   "自分の体質を理解して、\n食事を適切に整える。\n遠回りに見えて、これが一番の近道です。"]),
 ("personality",["人は、快適な場所から\n出たくない生き物です。",
   "コンフォートゾーンと言います。\n今までと同じ決断を続ける限り、\n今までと同じ結果しか出ません。\n耳が痛い話かもしれません。",
   "でも、何かを変えたいなら\n決断を1つ変えるだけでいいのです。\n小さな一歩からで大丈夫です。"]),
]
def main():
    p=os.path.join(DIR,"content_bank.json")
    bank=json.load(open(p,encoding="utf-8"))
    ex={t["segments"][0].split("\n")[0].strip() for t in bank}
    n=0
    for cat,segs in T:
        if segs[0].split("\n")[0].strip() in ex: continue
        bank.append({"type":"live","cat":cat,"segments":list(segs)}); n+=1
    json.dump(bank,open(p,"w"),ensure_ascii=False,indent=1)
    print(f"6/21 LIVE由来 {n}本追加 / バンク計 {len(bank)}")
if __name__=="__main__": main()
