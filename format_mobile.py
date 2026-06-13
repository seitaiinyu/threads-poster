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


def split_eq(line):
    """行中の ＝ / → の前で改行（A＝B＝C → 各行に）。先頭の連結記号は保持。"""
    if "＝" not in line and "→" not in line:
        return [line]
    out = re.split(r"(?=[＝→])", line)
    return [s for s in out if s]


def split_long(line):
    """長い行を、まず ＝/→ 連結で折り、次に句点(。!?)、最後に読点(、)で折る。"""
    if is_list(line) or len(line) <= MAX:
        return [line]
    result = []
    for part in split_eq(line):
        if len(part) <= MAX:
            result.append(part)
            continue
        for p in _split_by(part, "。！？", 1):  # 文単位
            if len(p) <= MAX:
                result.append(p)
            else:
                result.extend(_split_by(p, "、", 8))  # 読点でさらに
    return result


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
