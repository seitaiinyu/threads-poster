import json
for fn, bak, idxs in (("content_bank_yu.json", "content_bank_yu.bak.json", [239, 245, 250, 253, 257, 262, 265, 272, 278, 285]),
                      ("content_bank.json", "content_bank.bak.json", [130, 133, 146, 151, 157, 162, 176, 201, 213, 224])):
    a = json.load(open("/private/tmp/claude-501/" + bak))
    b = json.load(open("/Users/takeuchiyuuki/threads-poster/" + fn))
    for i in idxs:
        print(fn, i)
        print("  BEFORE:", a[i]["segments"][0].replace("\n", " / "))
        print("  AFTER :", b[i]["segments"][0].replace("\n", " / "))
