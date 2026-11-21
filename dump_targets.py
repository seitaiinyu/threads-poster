import json
import sys

OUT = "/private/tmp/claude-501/-Users-takeuchiyuuki-Desktop/6696760f-39af-4f70-8e47-25075c697184/scratchpad/targets.txt"
specs = [
    ("/Users/takeuchiyuuki/threads-poster/content_bank_yu.json", ["yt"]),
    ("/Users/takeuchiyuuki/threads-poster/content_bank.json", ["live", "igai", "rapport", "bui"]),
]
lines = []
for path, types in specs:
    data = json.load(open(path, encoding="utf-8"))
    tag = "YU" if "_yu" in path else "DI"
    for i, e in enumerate(data):
        if e.get("type") in types:
            segs = e["segments"]
            lines.append("=== %s #%d type=%s n=%d" % (tag, i, e["type"], len(segs)))
            for k in (1, 2):
                if k < len(segs):
                    lines.append("--- seg%d" % k)
                    lines.append(segs[k])
open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print(len(lines))
