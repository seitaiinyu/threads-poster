#!/usr/bin/env python3
"""診断誘導を1日2本(朝・夜)運用にするため本数を追加し、ツリー2投稿目に診断リンクを置く。
リンクは自分のWebアプリ(netlify)のみ。lin.ee等の直リンクは貼らない。"""
import json, os
DIR = os.path.dirname(os.path.abspath(__file__))
URL = "https://youtsu-shindan.netlify.app"

ADD = [
 ("腰痛が「朝いちばん」につらい人と、\n「夕方」につらい人。\n原因は別物です。",
  "朝→寝具や寝姿勢。\n夕方→日中の姿勢の蓄積。\nいつ痛むかで、\n打つ手がまったく変わります。"),
 ("腰痛のケアで遠回りする人の共通点。",
  "それは「人気のストレッチ」から入ることです。\n合うタイプの人には効きますが、\n合わない人には逆効果になります。"),
 ("あなたの腰は、\n「丸まって痛む」タイプですか。\n「反って痛む」タイプですか。",
  "靴下を履く時につらいなら丸まりタイプ。\n長く立つとつらいなら反りタイプ。\n必要なケアは正反対です。"),
 ("腰痛の原因が「お尻」の人と、\n「お腹」の人がいます。",
  "お尻が硬いと骨盤が動かず、\nお腹の力が抜けると腰が支えられません。\nどちらが原因かで\nやるべきことが変わります。"),
 ("腰痛を何年も繰り返している人へ。\n一度、原因を整理しませんか。",
  "その場しのぎを続けると、\n何が効いて何が効かないのか\n分からないままになります。\nまず現在地を知ることです。"),
 ("腰痛のセルフケア、\n「効いている実感」がありますか。",
  "効かないなら、\n頑張りが足りないのではなく\nタイプが合っていない可能性があります。"),
 ("デスクワークの腰痛と、\n立ち仕事の腰痛は別物です。",
  "座位は椎間板に、\n立位は腰の関節に負担がかかります。\n同じ「腰痛」でも\n原因の場所が違います。"),
]

def main():
    p=os.path.join(DIR,"content_bank_yu.json")
    bank=json.load(open(p,encoding="utf-8"))
    ex={t["segments"][0].split("\n")[0].strip() for t in bank}
    GUIDES=[t["segments"][-1] for t in bank if t.get("shindan")]
    n=0
    for i,(h,e) in enumerate(ADD):
        if h.split("\n")[0].strip() in ex: continue
        bank.append({"type":"shindan","cat":"participation","shindan":True,
                     "disease":"腰痛","segments":[h,e,GUIDES[i%len(GUIDES)]]}); n+=1
    # 全診断投稿の2段目末尾に診断リンクを付与（ツリー2投稿目＝返信扱いで抑制を受けにくい）
    k=0
    for t in bank:
        if not t.get("shindan"): continue
        s=t["segments"][1]
        if URL not in s:
            t["segments"][1]=s+f"\n\n▼5問・約30秒の無料診断\n{URL}"; k+=1
    json.dump(bank,open(p,"w"),ensure_ascii=False,indent=1)
    print(f"診断投稿 {n}本追加 / 2段目にリンク付与 {k}本 / 診断計 {sum(1 for t in bank if t.get('shindan'))}")

if __name__=="__main__": main()
