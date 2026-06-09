#!/usr/bin/env python3
import os, json, time, urllib.request, urllib.parse, statistics
from datetime import datetime, timezone, timedelta
from collections import defaultdict

API="https://graph.threads.net/v1.0"
TOK=os.environ["THREADS_ACCESS_TOKEN"]
JST=timezone(timedelta(hours=9))

posts=json.load(open("posts_90d.json"))
# TEXT/IMAGEのみ（再投稿facadeは除外）
posts=[p for p in posts if p.get("media_type") in ("TEXT_POST","IMAGE")]
# 均等サンプリング ~450件
step=max(1, len(posts)//450)
sample=posts[::step]

def views(mid):
    url=f"{API}/{mid}/insights?metric=views&access_token="+urllib.parse.quote(TOK)
    try:
        with urllib.request.urlopen(url) as r: d=json.loads(r.read().decode())
        for m in d.get("data",[]):
            if m["name"]=="views":
                v=m.get("values",[{}])
                return v[0].get("value",0) if v else 0
    except Exception as e:
        return None
    return 0

rows=[]
log=open("sample_progress.txt","w")
for i,p in enumerate(sample,1):
    ts=datetime.strptime(p["timestamp"],"%Y-%m-%dT%H:%M:%S%z").astimezone(JST)
    v=views(p["id"])
    if v is not None:
        rows.append((ts.hour, ts.weekday(), v))
    if i%50==0:
        log.write(f"{i}/{len(sample)}\n"); log.flush()
    time.sleep(0.03)

json.dump(rows, open("time_rows.json","w"))

hour=defaultdict(list)
for h,wd,v in rows: hour[h].append(v)

out=[]
out.append(f"サンプル数: {len(rows)} / 母集団 {len(posts)}件")
out.append("\n=== 時間帯別 平均閲覧数（JST, 平均降順）===")
out.append(f"{'時':>4} | {'件数':>4} | {'平均閲覧':>8} | {'中央値':>7} | {'最大':>7}")
summ=[]
for h in range(24):
    vs=hour.get(h,[])
    if vs: summ.append((h,len(vs),statistics.mean(vs),statistics.median(vs),max(vs)))
mx=max(s[2] for s in summ)
for h,n,avg,med,m in sorted(summ,key=lambda x:-x[2]):
    bar="#"*int(avg/mx*25)
    out.append(f"{h:>2}時 | {n:>4} | {avg:>8.0f} | {med:>7.0f} | {m:>7} {bar}")

out.append("\n=== 時間ブロック別 平均閲覧数 ===")
blocks={"早朝 5-8時":range(5,9),"午前 9-11時":range(9,12),"昼 12-14時":range(12,15),
        "午後 15-17時":range(15,18),"夜 18-21時":range(18,22),"深夜 22-翌4時":list(range(22,24))+list(range(0,5))}
bl=[]
for name,hrs in blocks.items():
    vs=[v for h in hrs for v in hour.get(h,[])]
    if vs: bl.append((name,len(vs),statistics.mean(vs)))
for name,n,avg in sorted(bl,key=lambda x:-x[2]):
    out.append(f"{name:>12}: {n:>4}件  平均閲覧 {avg:>8.0f}")

res="\n".join(out)
open("time_result.txt","w").write(res)
print(res)
