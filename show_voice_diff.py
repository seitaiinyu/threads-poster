import json
import sys

b = json.load(open("/Users/takeuchiyuuki/threads-poster/rewrite_voice_before.json", encoding="utf-8"))
yu = json.load(open("/Users/takeuchiyuuki/threads-poster/content_bank_yu.json", encoding="utf-8"))
di = json.load(open("/Users/takeuchiyuuki/threads-poster/content_bank.json", encoding="utf-8"))
same = []
for key, v in b.items():
    d = yu if key.startswith("YU") else di
    i = int(key[2:])
    for k in (0, 1):
        if d[i]["segments"][k + 1] == v[k]:
            same.append((key, k + 1))
print("unchanged", len(same), same)
for key in sys.argv[1:]:
    d = yu if key.startswith("YU") else di
    i = int(key[2:])
    print("##", key)
    print("BEFORE\n" + b[key][0])
    print("AFTER\n" + d[i]["segments"][1])
for w in ["ぶっちゃけ", "正直に言うと", "じゃないですか"]:
    c = sum(1 for key in b for k in (1, 2) if w in (yu if key.startswith("YU") else di)[int(key[2:])]["segments"][k])
    print(w, c)
