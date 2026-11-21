import json
import hashlib
import re

SCR = "/private/tmp/claude-501/-Users-takeuchiyuuki-Desktop/6696760f-39af-4f70-8e47-25075c697184/scratchpad"
BASE = "/Users/takeuchiyuuki/threads-poster"
SPEC = [
    ("YU", BASE + "/content_bank_yu.json", SCR + "/orig_yu.json", ["yt"]),
    ("DI", BASE + "/content_bank.json", SCR + "/orig_di.json", ["live", "igai", "rapport", "bui"]),
]
BAD = ["しましょう", "すべき", "ではありません", "存在しません", "私", "方へ", "人へ", "必ず", "100%",
       "のです", "のである", "ことが多いです", "可能性があります"]


def h(x):
    return hashlib.md5(json.dumps(x, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


tot = 0
bad = 0
changed = 0
long_lines = 0
for tag, path, orig, types in SPEC:
    a = json.load(open(path, encoding="utf-8"))
    b = json.load(open(orig, encoding="utf-8"))
    assert len(a) == len(b)
    for i, (x, y) in enumerate(zip(a, b)):
        tgt = x.get("type") in types
        if not tgt:
            assert h(x) == h(y), (tag, i)
            continue
        tot += 1
        assert x.keys() == y.keys()
        assert len(x["segments"]) == len(y["segments"])
        for k in range(len(x["segments"])):
            if k not in (1, 2):
                assert x["segments"][k] == y["segments"][k], (tag, i, k)
        for k in (1, 2):
            s = x["segments"][k]
            if s != y["segments"][k]:
                changed += 1
            for w in BAD:
                if w in s:
                    bad += 1
                    print("BAD", tag, i, k, w)
            # bullet count preserved
            assert s.count("\n・") + s.startswith("・") == y["segments"][k].count("\n・") + y["segments"][k].startswith("・"), (tag, i, k, "bullets")
            for ln in s.split("\n"):
                if len(ln) > 30 and not ln.startswith("・"):
                    long_lines += 1
print("targets", tot, "changed segs", changed, "bad", bad, "long lines", long_lines)
