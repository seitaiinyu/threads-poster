#!/usr/bin/env python3
"""投稿をコンパクトに整形：空行を除去して単一改行に。
短い文（10文字以下で。！？終わり）は次の通常行と同じ行にまとめる。
リスト行(・＝→①等)は維持。"""
import json, os, re, sys

DIR = os.path.dirname(os.path.abspath(__file__))
LIST_PREFIX = ("・", "＝", "→", "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "▶", "✔", "❌", "⭕")


def is_list(s):
    return s.lstrip().startswith(LIST_PREFIX)


def fmt(seg):
    # 空行を除去（単一改行のみ残す）
    lines = [l.strip() for l in seg.split("\n") if l.strip() != ""]
    merged = []
    i = 0
    while i < len(lines):
        cur = lines[i]
        # 短い文（句点終わり・10字以下）＋次が通常行 → まとめる
        if (i + 1 < len(lines) and len(cur) <= 10 and cur.endswith(("。", "！", "？"))
                and not is_list(cur) and not is_list(lines[i + 1])):
            merged.append(cur + lines[i + 1])
            i += 2
        else:
            merged.append(cur)
            i += 1
    return "\n".join(merged).strip()


def main():
    apply = "--apply" in sys.argv
    for fn in ["content_bank.json", "content_bank_yu.json"]:
        p = os.path.join(DIR, fn)
        bank = json.load(open(p, encoding="utf-8"))
        if not apply:
            print(f"===== {fn} プレビュー（先頭2ツリーの1段目）=====")
            for t in bank[:2]:
                print("--- 整形後 ---")
                print(fmt(t["segments"][0]))
                print()
            continue
        for t in bank:
            t["segments"] = [fmt(s) for s in t["segments"]]
        json.dump(bank, open(p, "w"), ensure_ascii=False, indent=1)
        print(f"{fn}: コンパクト整形して保存（{len(bank)}ツリー）")


if __name__ == "__main__":
    main()
