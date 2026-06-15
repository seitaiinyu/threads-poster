#!/usr/bin/env python3
"""事例の地域名を、越谷院に通える近隣エリアのみに統一。
対象: 「○○在住」「【○○市/町】」。CTAの『越谷で…』(院の所在地)はそのまま。"""
import json, os, re, sys

DIR = os.path.dirname(os.path.abspath(__file__))
BARE = ["越谷", "草加", "吉川", "さいたま", "松伏", "川口"]   # 在住用
FULL = ["越谷市", "草加市", "吉川市", "さいたま市", "松伏町", "川口市"]  # 【】用


def fix_text(text, ctr):
    # 「○○在住」の○○を近隣に置換
    def repl_zaiju(m):
        city = BARE[ctr[0] % len(BARE)]; ctr[0] += 1
        return city + "在住"
    text = re.sub(r"[一-龥ぁ-んァ-ヶー]{2,4}在住", repl_zaiju, text)
    # 「【○○市】「【○○町】」を近隣に置換
    def repl_brk(m):
        city = FULL[ctr[0] % len(FULL)]; ctr[0] += 1
        return "【" + city + "】"
    text = re.sub(r"【[一-龥ぁ-んァ-ヶー]{2,5}[市町区]】", repl_brk, text)
    return text


def process(fn):
    p = os.path.join(DIR, fn)
    bank = json.load(open(p, encoding="utf-8"))
    ctr = [0]; changed = 0
    for t in bank:
        new = []
        for s in t["segments"]:
            f = fix_text(s, ctr)
            if f != s:
                changed += 1
            new.append(f)
        t["segments"] = new
        if "cta" in t:
            t["cta"] = fix_text(t["cta"], ctr)
    json.dump(bank, open(p, "w"), ensure_ascii=False, indent=1)
    print(f"{fn}: 地域名を近隣に統一（{changed}段で置換）")


if __name__ == "__main__":
    for fn in ["content_bank_yu.json", "content_bank.json"]:
        process(fn)
