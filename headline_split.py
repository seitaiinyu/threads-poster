#!/usr/bin/env python3
"""1投稿目(見出し)をスマホ向けに改行する。
1行が HMAX 字を超える行は、まず読点(、)で、次に助詞の後ろ(中央に近い位置)で2行に分ける。
usage: python3 headline_split.py [--apply]"""
import json, os, re, sys
DIR = os.path.dirname(os.path.abspath(__file__))
HMAX = 18  # 見出し1行の目安
PARTICLES = "がはをにでともへ"


def split_line(line):
    line = line.strip()
    if len(line) <= HMAX:
        return [line]
    # 1) 読点で分ける（読点は前の行の末尾に残す）
    if "、" in line:
        parts = [p for p in re.split(r"(?<=、)", line) if p]
        out, buf = [], ""
        for p in parts:
            if buf and len(buf) + len(p) > HMAX:
                out.append(buf); buf = p
            else:
                buf += p
        if buf:
            out.append(buf)
        if all(len(x) <= HMAX + 4 for x in out) and len(out) >= 2:
            return [y for x in out for y in split_line(x)] if any(len(x) > HMAX + 4 for x in out) else out
    # 2) 中央に近い助詞の後ろで分ける
    mid = len(line) // 2
    best = None
    for i, ch in enumerate(line):
        if ch in PARTICLES and 5 <= i + 1 <= len(line) - 5:
            if best is None or abs(i + 1 - mid) < abs(best - mid):
                best = i + 1
    if best:
        return split_line(line[:best]) + split_line(line[best:])
    return [line]


def fmt_head(seg):
    lines = [l for l in seg.split("\n")]
    out = []
    for l in lines:
        if l.strip() == "":
            out.append("")
        else:
            out.extend(split_line(l))
    return "\n".join(out).strip()


def main():
    apply = "--apply" in sys.argv
    for fn in ["content_bank.json", "content_bank_yu.json"]:
        p = os.path.join(DIR, fn)
        bank = json.load(open(p, encoding="utf-8"))
        changed = 0; shown = 0
        for t in bank:
            new = fmt_head(t["segments"][0])
            if new != t["segments"][0]:
                changed += 1
                if shown < 6:
                    print("前:", t["segments"][0].replace("\n", " / "))
                    print("後:", new.replace("\n", " / ")); print()
                    shown += 1
                if apply:
                    t["segments"][0] = new
        if apply:
            json.dump(bank, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{fn}: 見出しを改行 {changed}/{len(bank)}本 {'保存' if apply else '(プレビュー)'}\n")


if __name__ == "__main__":
    main()
