#!/usr/bin/env python3
"""投稿の改行を見やすく整形。文末(。！？)の後の新しい文との間に空行を入れる。
リスト行(・/①②/＝/→ で始まる、または前行から続く列挙)は詰めたまま維持。"""
import json, os, re, sys

DIR = os.path.dirname(os.path.abspath(__file__))
LIST_PREFIX = ("・", "＝", "→", "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "▶")


def is_list_line(s):
    return s.lstrip().startswith(LIST_PREFIX)


def fmt(seg):
    # 改行を正規化
    lines = [l.rstrip() for l in seg.split("\n")]
    # 連続する空行は1つに
    out = []
    prev_blank = False
    for l in lines:
        if l == "":
            if not prev_blank and out:
                out.append("")
            prev_blank = True
        else:
            out.append(l)
            prev_blank = False
    # 文末の後に新しい文が続く場合、空行を挿入（リスト行は除く）
    result = []
    for i, l in enumerate(out):
        result.append(l)
        if i + 1 < len(out):
            cur, nxt = l, out[i + 1]
            if cur and nxt and cur.endswith(("。", "！", "？", "…")) \
               and not is_list_line(nxt) and not is_list_line(cur):
                # すでに空行が次にあるならスキップ
                if nxt != "":
                    result.append("")
    # 整理（先頭末尾の空行除去、連続空行を1つに）
    text = "\n".join(result)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def process(fn, preview=False):
    p = os.path.join(DIR, fn)
    bank = json.load(open(p, encoding="utf-8"))
    samples = []
    for t in bank:
        new = [fmt(s) for s in t["segments"]]
        if preview and len(samples) < 2:
            samples.append((t["segments"][0], new[0]))
        t["segments"] = new
    if preview:
        return samples, bank
    json.dump(bank, open(p, "w"), ensure_ascii=False, indent=1)
    return None, bank


if __name__ == "__main__":
    preview = "--apply" not in sys.argv
    for fn in ["content_bank.json", "content_bank_yu.json"]:
        samples, bank = process(fn, preview=preview)
        if preview:
            print(f"===== {fn} プレビュー =====")
            # 整形で変化した本文段を1つ探して表示
            b = json.load(open(os.path.join(DIR, fn), encoding="utf-8"))
            shown = 0
            for t in b:
                for s in t["segments"]:
                    f = fmt(s)
                    if f != s and "\n" in s and shown < 2:
                        print("--- 変更前 ---"); print(s)
                        print("--- 変更後 ---"); print(f); print()
                        shown += 1
                if shown >= 2:
                    break
        else:
            print(f"{fn}: 整形して保存しました（{len(bank)}ツリー）")
