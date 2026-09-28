#!/usr/bin/env python3
"""「週末」フックの常緑投稿(金土日のみ配信 wd=[4,5,6])。日曜夜ネタは日曜のみ。"""
import json, os
DIR = os.path.dirname(os.path.abspath(__file__))
FRI_SUN=[4,5,6]; SUN=[6]; MON=[0]

DIET=[
 (FRI_SUN,"empathy",["平日は順調なのに、\n週末だけ太るあなたへ。",
   "平日の我慢の反動で、\n週末に食のタガが外れる。\n5日かけて減らした分を\n2日で戻すパターンです。",
   "我慢をやめるのが正解です。\n平日から適量をきちんと食べれば、\n週末の反動は起きにくくなります。"]),
 (FRI_SUN,"education",["週末の「ごほうび外食」、\n食べる前の30秒で結果が変わります。",
   "・先に水を1杯\n・サラダやスープから\n・ご飯は最後に\nこれだけで血糖値の急上昇が抑えられ、\n同じ食事でもためこみにくくなります。",
   "我慢せず、順番だけ変える。\n今夜から使えるテクニックです。"]),
 (FRI_SUN,"education",["週末の寝だめ、\n実は太りやすくなります。",
   "起床時間が2〜3時間ズレると\n体内時計が乱れ、\n食欲のホルモンまで乱れます。\n月曜に食欲が暴れる原因はこれです。",
   "起きる時間はいつも通りに。\n眠ければ昼寝20分で調整してください。"]),
 (SUN,"empathy",["日曜の夜、\n「明日からダイエット頑張る」と\n思っているあなたへ。",
   "その決意、先週もしませんでしたか。\n月曜リセット癖は、\n目標が大きすぎるサインです。",
   "「明日から頑張る」をやめて、\n「今夜、体重計に乗る」だけにする。\n小さすぎる一歩が、一番続きます。"]),
 (MON,"education",["週末に増えた体重は、\n月曜の過ごし方で決まります。",
   "増えた直後はまだ食べ物の重さと\nむくみの段階です。\n月曜に普段の食事とリズムへ\n戻せれば、脂肪になる前に消えます。",
   "・朝いつも通りに起きる\n・水を多めに\n・食事の間隔をしっかり空ける"]),
]
YU=[
 (FRI_SUN,"腰痛",["週末の作り置きや大掃除、\n終わった後に腰が固まっていませんか。",
   "中腰と立ちっぱなしが続くと、\n腰の一点に負担が積み重なります。\n家事は立派な「長時間労働」です。",
   "・20分ごとに一度伸びをする\n・片膝をついて低い場所の作業を\n・終わったら湯船で温める"]),
 (FRI_SUN,"坐骨",["週末にまとめてやる「運動」が、\n坐骨神経痛を悪化させることがあります。",
   "平日動かない体で急に長時間動くと、\nお尻の筋肉が対応できず\n神経を圧迫しやすくなります。",
   "・運動は「週末だけ長く」より「毎日短く」\n・始める前に股関節を回す\n・痛みが出たら中断する勇気を"]),
 (SUN,"腰痛",["日曜の夜に腰が重いのは、\n「休みすぎ」かもしれません。",
   "ソファで長く座る、昼まで寝る。\n休日の「動かない時間」は\n腰の血流を落として固めます。",
   "月曜の朝がつらい人は、\n日曜の夜に5分だけ、\nお尻と太もも裏を伸ばしてみてください。"]),
]

def main():
    p=os.path.join(DIR,"content_bank.json"); b=json.load(open(p,encoding="utf-8"))
    ex={t["segments"][0].split("\n")[0].strip() for t in b}
    n=0
    for wd,cat,segs in DIET:
        if segs[0].split("\n")[0].strip() in ex: continue
        b.append({"type":"weekend","cat":cat,"cta":"","wd":wd,"segments":list(segs)}); n+=1
    json.dump(b,open(p,"w"),ensure_ascii=False,indent=1); print(f"A1 週末ネタ{n}本 / 計{len(b)}")
    p=os.path.join(DIR,"content_bank_yu.json"); b=json.load(open(p,encoding="utf-8"))
    ex={t["segments"][0].split("\n")[0].strip() for t in b}
    n=0
    for wd,dz,segs in YU:
        if segs[0].split("\n")[0].strip() in ex: continue
        b.append({"type":"weekend","cat":"empathy","disease":dz,"wd":wd,
                  "segments":list(segs)+["越谷の整体院 優-YU- では\n腰痛・坐骨神経痛のご相談を受けています。\n詳しくはプロフィールをご覧ください。"]}); n+=1
    json.dump(b,open(p,"w"),ensure_ascii=False,indent=1); print(f"A2 週末ネタ{n}本 / 計{len(b)}")

if __name__=="__main__": main()
