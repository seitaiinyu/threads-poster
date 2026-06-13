#!/usr/bin/env python3
"""アカウント1のツリーを3部構成に統一：①フック ②共感・教育 ③まとめ。
各ツリーから 先頭(フック)・2段目(教育)・最後の内容段(まとめ) を抽出。
CTA段は別途 cta フィールドに保持（回復期は投稿されない/将来CTA再開時に③へ）。"""
import json, os, sys
DIR = os.path.dirname(os.path.abspath(__file__))


def is_cta(seg):
    return ("プロフィール" in seg) or ("公式LINE" in seg)


def to_3part(segs):
    cta = None
    body = list(segs)
    if body and is_cta(body[-1]):
        cta = body[-1]
        body = body[:-1]
    if len(body) <= 3:
        return body, cta
    hook = body[0]
    # ③まとめ: 「・」を含む実践リストを優先（なければ最後の段）
    list_idxs = [i for i in range(1, len(body)) if "・" in body[i]]
    summ_idx = list_idxs[-1] if list_idxs else len(body) - 1
    summary = body[summ_idx]
    # ②教育: フックとまとめの間で最も内容の濃い（長い）段。無ければ2段目
    mids = [body[i] for i in range(1, summ_idx)]
    edu = max(mids, key=len) if mids else body[1]
    return [hook, edu, summary], cta


def main():
    apply = "--apply" in sys.argv
    p = os.path.join(DIR, "content_bank.json")
    bank = json.load(open(p, encoding="utf-8"))
    if not apply:
        shown = 0
        for t in bank:
            if len(t["segments"]) >= 6 and shown < 2:
                three, cta = to_3part(t["segments"])
                print("=== 変更前（段数", len(t["segments"]), ")===")
                for i, s in enumerate(t["segments"], 1):
                    print(f"[{i}]", s.replace("\n", " ")[:46])
                print("--- 3部構成（後）---")
                for i, s in enumerate(three, 1):
                    print(f"[{i}]", s.replace("\n", " ")[:46])
                print()
                shown += 1
        return
    for t in bank:
        three, cta = to_3part(t["segments"])
        t["segments"] = three
        if cta:
            t["cta"] = cta
    json.dump(bank, open(p, "w"), ensure_ascii=False, indent=1)
    print(f"アカウント1を3部構成に統一: {len(bank)}ツリー")


if __name__ == "__main__":
    main()
