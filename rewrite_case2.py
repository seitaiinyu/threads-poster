import json
import os
import re

PATH = os.path.expanduser("~/threads-poster/content_bank.json")

# 画像ID -> (新しい1投稿目, 2投稿目の冒頭1行)
NEW = {
    "Df4Z9c6EwqT.jpg": ("更年期で健診の数字が悪化していた人が\n後回しをやめて変わったこと",
                        "写真の方は、3ヶ月でウエスト−7cm、体重は−7kg変わりました。"),
    "Dfrf0rxE9k7.jpg": ("健診が憂鬱で仕方なかった人が\n最後にやめた、たった一つのこと",
                        "写真の方は、3ヶ月で−8.1kg変わりました。"),
    "Dfjxm8vE6lm.jpg": ("ジムも断食も続かなかった人が\n選んだのは普段のご飯",
                        "写真の方は、こんなに変わりました。"),
    "DbW_5LGkwO0.jpg": ("リバウンド続きだった人が\n最初に手をつけた場所",
                        "写真の方は、半年で−14.2kg変わりました。"),
    "DcnmeC8ETCO.jpg": ("旅行の写真が怖かった人が\n我慢をやめて変わったこと",
                        "写真の方は、3ヶ月で−10.4kg変わりました。"),
    "DbXAQd7k9c5.jpg": ("外食もお酒もやめなかった更年期の人に\n健診で起きたこと",
                        "写真の方は、3ヶ月で−7.3kg変わりました。"),
    "Dep0PZYE0B4.jpg": ("健診の頃から増え続けた人が\nカロリー計算なしで変われた理由",
                        "写真の方は、3ヶ月で−5kg変わりました。"),
    "DbAQn1HEV73.jpg": ("何をやっても減らなかった人が\n最後にやめたのは我慢でした",
                        "写真の方は、3ヶ月で−10.9kg変わりました。"),
    "DbXBVFVk5bM.jpg": ("運動を頑張ってもリバウンドした人が\n方向を変えたら起きたこと",
                        "写真の方は、−13.8kgまで変わりました。"),
    "DbXAEAGk0Ws.jpg": ("運動をしなくても変われた人が\n変えたのは別のところ",
                        "写真の方は、3ヶ月で−7.3kg変わりました。"),
    "De9IiNyE-Ee.jpg": ("腰が痛くて子どもと遊べなかった母が\n家族と同じご飯で変わった話",
                        "写真の方は、3ヶ月で−6.2kg変わりました。"),
    "De3JBStE_Xb.jpg": ("ベルトの穴が変わった男性が\n外食をやめなかった理由",
                        "写真の方は、3ヶ月で−6.2kg変わりました。"),
    "DZqyYVIEz9Q.jpg": ("合う服がなくなっていた人に\n髪と肌まで起きた変化",
                        "写真の方は、3ヶ月で−9.4kg変わりました。"),
    "Dc0hAPJk0lT.jpg": ("旅行もお酒の席も我慢しなかった人の\n体質の話",
                        "写真の方は、4ヶ月で−7.1kg変わりました。"),
    "DZtG0rCE9B8.jpg": ("リバウンドが怖くて動けなかった人が\n半年後に始めたこと",
                        "写真の方は、半年で−14.2kg変わりました。"),
    "DfE30PgEy17.jpg": ("健診で病院行きが迫っていた母の\n腰まで軽くなった話",
                        "写真の方は、3ヶ月で−6.2kg変わりました。"),
}

BAN = ["のです", "しましょう", "すべき", "方へ", "人へ", "http"]


def main():
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)

    done = 0
    for x in data:
        if x.get("type") != "case2":
            continue
        img = x.get("image")
        if img not in NEW or x.get("_rewritten"):
            continue
        head, intro = NEW[img]
        segs = x["segments"]
        if intro in segs[1]:
            continue
        segs[0] = head
        segs[1] = intro + "\n\n" + segs[1]
        done += 1

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)

    print("rewritten:", done)
    mx = 0
    for x in data:
        if x.get("type") != "case2":
            continue
        s = x["segments"]
        print(repr(s[0]))
        mx = max(mx, len(s[0]))
        if re.search(r"[0-9０-９]", s[0]):
            print("  !! digit in segments[0]")
        for i, t in enumerate(s):
            if len(t) > 300:
                print("  !! too long", i, len(t))
            for b in BAN:
                if b in t:
                    print("  !! banned", b, i)
        if len(s[0]) > 40:
            print("  !! headline over 40")
    print("max segments[0] length:", mx)


main()
