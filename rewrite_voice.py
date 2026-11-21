import json
import glob
import hashlib
import re
import shutil

SCR = "/private/tmp/claude-501/-Users-takeuchiyuuki-Desktop/6696760f-39af-4f70-8e47-25075c697184/scratchpad"
BASE = "/Users/takeuchiyuuki/threads-poster"
FILES = {"YU": BASE + "/content_bank_yu.json", "DI": BASE + "/content_bank.json"}
TYPES = {"YU": ["yt"], "DI": ["live", "igai", "rapport", "bui"]}
BEFORE = BASE + "/rewrite_voice_before.json"

# 1. 新テキストの読み込み
new = {}
for fn in sorted(glob.glob(SCR + "/out_*.txt")):
    text = open(fn, encoding="utf-8").read()
    cur = None
    seg = None
    buf = []

    def flush():
        if cur is not None and seg is not None:
            new[cur][seg] = "\n".join(buf).strip("\n")

    for line in text.split("\n"):
        m = re.match(r"^=== (YU|DI) #(\d+) ", line)
        if m:
            flush()
            cur = (m.group(1), int(m.group(2)))
            new[cur] = {}
            seg = None
            buf = []
        elif line in ("--- seg1", "--- seg2"):
            flush()
            seg = int(line[-1])
            buf = []
        else:
            buf.append(line)
    flush()

# 2. 適用
before = {}
for tag, path in FILES.items():
    data = json.load(open(path, encoding="utf-8"))
    orig_hash = {}
    for i, e in enumerate(data):
        if e.get("type") in TYPES[tag]:
            key = (tag, i)
            assert key in new, key
            assert 1 in new[key] and 2 in new[key], key
            before[tag + str(i)] = [e["segments"][1], e["segments"][2]]
            e["segments"][1] = new[key][1]
            e["segments"][2] = new[key][2]
    shutil.copy(path, path + ".bak_voice") if False else None
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

json.dump(before, open(BEFORE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("applied", sum(len(v) for v in new.values()) // 2)
