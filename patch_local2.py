#!/usr/bin/env python3
"""地域枠の変更: ①あるある型(local2)を旧地域投稿より優先 ②A1の地域枠を毎日(夜の最終枠)に。"""
import os
DIR = os.path.dirname(os.path.abspath(__file__))
ap = os.path.join(DIR, "auto_post.py")
s = open(ap, encoding="utf-8").read()
old1 = """    if pick is None and want_local:
        for off in range(n):
            t = bank[(state["idx"] + off) % n]
            if t.get("local") and dz_ok(t) and hook_of(t) not in seen:
                pick = (state["idx"] + off) % n; break
"""
new1 = """    if pick is None and want_local:
        # 越谷あるある型(local2)を先に、無ければ旧地域型
        for need2 in (True, False):
            for off in range(n):
                t = bank[(state["idx"] + off) % n]
                if t.get("local") and (t.get("type") == "local2") == need2 and dz_ok(t) and hook_of(t) not in seen:
                    pick = (state["idx"] + off) % n; break
            if pick is not None:
                break
"""
old2 = 'want_local = local_every > 0 and state["count"] == cap - 1 and day_num % 2 == 0'
new2 = 'want_local = local_every > 0 and state["count"] == cap - 1  # 毎日1本(夜の最終枠)'
assert old1 in s and old2 in s
s = s.replace(old1, new1).replace(old2, new2)
open(ap, "w", encoding="utf-8").write(s)
print("patched")
