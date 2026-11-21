import json
d = json.load(open('/Users/takeuchiyuuki/threads-poster/draft_cases_diet.json'))
ng = ["しましょう","すべき","ではありません","存在しません","私","方へ","人へ","必ず","100%","のです","ことが多いです","可能性があります","において","によって","誰でも"]
print(len(d), sum(1 for x in d if x["shindan"]))
for i, x in enumerate(d, 1):
    s = x["segments"]
    l = s[0].split("\n")
    flag = []
    if len(s) != 3: flag.append("segcount")
    if len(l) != 2 or not (13 <= len(l[0]) <= 22) or not (10 <= len(l[1]) <= 18) or len(l[0]) + len(l[1]) > 40:
        flag.append("p1")
    for t in s:
        for w in ng:
            if w in t: flag.append("NG:" + w)
    c2 = len(s[1].replace("\n", ""))
    c3 = len(s[2].replace("\n", ""))
    b = sum(t.count("僕") for t in s)
    sh = "診断" in s[2]
    if sh != x["shindan"]: flag.append("shindan-mismatch")
    print(i, len(l[0]), len(l[1]) if len(l) > 1 else None, c2, c3, b, flag)
