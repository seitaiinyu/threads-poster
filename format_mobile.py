#!/usr/bin/env python3
"""スマホで読みやすい改行に整形。
長い行は読点(、)や区切りで分割し、1行を約20文字以内に収めて
途中での不自然な折り返しを防ぐ。リスト行(・＝→①等)はそのまま。"""
import json, os, re, sys

DIR = os.path.dirname(os.path.abspath(__file__))
MAX = 20  # 1行の目安（全角文字数）
LIST_PREFIX = ("・", "＝", "→", "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "▶", "✔", "❌", "⭕")


def is_list(s):
    return s.lstrip().startswith(LIST_PREFIX)


def _split_by(line, seps, min_len):
    out, buf = [], ""
    for ch in line:
        buf += ch
        if ch in seps and len(buf) >= min_len:
            out.append(buf); buf = ""
    if buf:
        out.append(buf)
    return out


def split_long(line):
    """長い行を、まず句点(。!?)で文単位に、まだ長ければ読点(、)で折る。"""
    if len(line) <= MAX or is_list(line):
        return [line]
    pieces = _split_by(line, "。！？", 1)  # 文単位
    out = []
    for p in pieces:
        if len(p) <= MAX:
            out.append(p)
        else:
            out.extend(_split_by(p, "、", 8))  # 読点でさらに分割
    return out


def fmt(seg):
    lines = [l.strip() for l in seg.split("\n") if l.strip() != ""]
    result = []
    for l in lines:
        result.extend(split_long(l))
    return "\n".join(result).strip()


def main():
    apply = "--apply" in sys.argv
    for fn in ["content_bank.json", "content_bank_yu.json"]:
        p = os.path.join(DIR, fn)
        bank = json.load(open(p, encoding="utf-8"))
        if not apply:
            print(f"===== {fn} プレビュー =====")
            shown = 0
            for t in bank:
                for s in t["segments"]:
                    f = fmt(s)
                    if f != s and shown < 3:
                        print("--- 前 ---"); print(s)
                        print("--- 後 ---"); print(f); print()
                        shown += 1
                if shown >= 3:
                    break
            continue
        for t in bank:
            t["segments"] = [fmt(s) for s in t["segments"]]
        json.dump(bank, open(p, "w"), ensure_ascii=False, indent=1)
        print(f"{fn}: スマホ向け整形して保存（{len(bank)}ツリー）")


if __name__ == "__main__":
    main()
