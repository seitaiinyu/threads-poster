import json
out = []
for fn, types in (("content_bank_yu.json", ["yt"]), ("content_bank.json", ["live", "igai", "rapport", "bui"])):
    d = json.load(open("/Users/takeuchiyuuki/threads-poster/" + fn))
    for i, x in enumerate(d):
        if x.get("type") in types:
            s = x["segments"]
            out.append("=== %s #%d type=%s cat=%s disease=%s nseg=%d" % (fn, i, x.get("type"), x.get("cat"), x.get("disease"), len(s)))
            out.append("[0] " + s[0])
            if len(s) > 1:
                out.append("[1] " + s[1][:80].replace("\n", "/"))
open("/Users/takeuchiyuuki/threads-poster/heads_dump.txt", "w").write("\n".join(out))
print(len(out))
