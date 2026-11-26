#!/usr/bin/env python3
"""画像を1投稿目ではなく2投稿目(image_at=1)に添付する形へ切り替える。
- publish_tree(segments, image, image_at) に拡張
- A/B(image_ab)は終了
- case2 16本に image_at=1 を設定"""
import json, os, re
DIR = os.path.dirname(os.path.abspath(__file__))
ap = os.path.join(DIR, "auto_post.py")
s = open(ap, encoding="utf-8").read()
s = s.replace('def publish_tree(segments, image=None):', 'def publish_tree(segments, image=None, image_at=0):')
s = s.replace('        if i == 0 and image:\n            p = {"media_type": "IMAGE"', '        if image and i == image_at:\n            p = {"media_type": "IMAGE"')
s = s.replace('time.sleep(8 if (i == 0 and image) else 2)', 'time.sleep(8 if (image and i == image_at) else 2)')
s = s.replace('    ids = publish_tree(segs, image)\n', '    ids = publish_tree(segs, image, int(tree.get("image_at", 0)))\n')
s = s.replace('"image_ab": True', '"image_ab": False')
open(ap, "w", encoding="utf-8").write(s)
assert 'image_at=0' in s and 'int(tree.get("image_at", 0))' in s and '"image_ab": False' in s
bp = os.path.join(DIR, "content_bank.json")
bank = json.load(open(bp, encoding="utf-8"))
n = 0
for t in bank:
    if t.get("type") == "case2" and t.get("image"):
        t["image_at"] = 1; n += 1
json.dump(bank, open(bp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("image_at=1 を設定:", n, "本 / コード更新OK")
