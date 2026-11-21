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


PARA_MAX = 3  # 1段落の最大行数


def paragraphs(lines):
    """行の並びを2〜3行の段落に分け、段落間に空行を入れる。
    ・文末(。！？)で段落を閉じる
    ・箇条書き(・①など)はまとめて1段落。箇条書きの前後では段落を切る
    ・3行を超えたら文末でなくても切る"""
    CHAIN = ("→", "＝")  # 前の行に続く連結記号。段落を割らない
    TERM = re.compile(r"([。！？!?…]|\d+\s*(回|秒|分|セット|kg|g))$")

    # 各行が「箇条書きの一部」かを判定（・で始まる行と、その折り返し行）
    listish = []
    for i, l in enumerate(lines):
        if is_list(l):
            listish.append(True)
        elif i > 0 and listish[-1] and not TERM.search(lines[i - 1]):
            listish.append(True)   # 前の箇条書きが文末で終わっていない＝折り返し
        else:
            listish.append(False)

    out, para = [], []
    for i, l in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        if para and listish[i] != listish[i - 1] and not l.startswith(CHAIN):
            out.append(para); para = []
        para.append(l)
        if listish[i] or (nxt is not None and nxt.startswith(CHAIN)):
            continue
        ends = l.endswith(("。", "！", "？", "!", "?", "…"))
        if (ends and len(para) >= 2) or len(para) >= PARA_MAX:
            out.append(para); para = []
    if para:
        out.append(para)
    return out


def fmt(seg):
    lines = [l.strip() for l in seg.split("\n") if l.strip() != ""]
    result = []
    for l in lines:
        result.extend(split_long(l))
    return "\n\n".join("\n".join(p) for p in paragraphs(result)).strip()


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
