import os, json, time, urllib.request, urllib.parse, statistics
from datetime import datetime, timezone, timedelta
from collections import defaultdict

API="https://graph.threads.net/v1.0"
TOK=os.environ["THREADS_ACCESS_TOKEN"]
JST=timezone(timedelta(hours=9))

posts=json.load(open("posts_yu_30d.json"))
posts=[p for p in posts if p.get("media_type") in ("TEXT_POST","IMAGE")]
step=max(1,len(posts)//450)
sample=posts[::step]

def insights(mid):
    url=f"{API}/{mid}/insights?metric=views,likes&access_token="+urllib.parse.quote(TOK)
    try:
        with urllib.request.urlopen(url) as r: d=json.loads(r.read().decode())
        out={}
        for m in d.get("data",[]):
            v=m.get("values",[{}])
            out[m["name"]]=v[0].get("value",0) if v else 0
        return out
    except Exception:
        return None

rows=[]
log=open("yu_progress.txt","w")
for i,p in enumerate(sample,1):
    ts=datetime.strptime(p["timestamp"],"%Y-%m-%dT%H:%M:%S%z").astimezone(JST)
    ins=insights(p["id"])
    if ins is not None:
        rows.append((ts.hour, ins.get("views",0), ins.get("likes",0)))
    if i%50==0: log.write(f"{i}/{len(sample)}\n"); log.flush()
    time.sleep(0.03)

json.dump(rows,open("yu_rows.json","w"))
hv=defaultdict(list); hl=defaultdict(list)
for h,v,l in rows: hv[h].append(v); hl[h].append(l)

out=[]
out.append(f"サンプル数: {len(rows)} / 母集団 {len(posts)}件")
out.append("\n=== 時間帯別（JST, 平均閲覧降順）===")
out.append(f"{'時':>3} | {'件数':>4} | {'平均閲覧':>8} | {'平均いいね':>9} | {'いいね率':>7}")
summ=[]
for h in range(24):
    if hv.get(h):
        av=statistics.mean(hv[h]); al=statistics.mean(hl[h])
        rate=(al/av*100) if av else 0
        summ.append((h,len(hv[h]),av,al,rate))
for h,n,av,al,rate in sorted(summ,key=lambda x:-x[2]):
    out.append(f"{h:>2}時 | {n:>4} | {av:>8.0f} | {al:>9.1f} | {rate:>6.1f}%")

out.append("\n=== 時間ブロック別 ===")
blocks={"早朝 5-8時":range(5,9),"午前 9-11時":range(9,12),"昼 12-14時":range(12,15),
        "午後 15-17時":range(15,18),"夜 18-21時":range(18,22),"深夜 22-翌4時":list(range(22,24))+list(range(0,5))}
for name,hrs in sorted(blocks.items(), key=lambda kv:-statistics.mean([v for h in kv[1] for v in hv.get(h,[0])] or [0])):
    vs=[v for h in hrs for v in hv.get(h,[])]; ls=[l for h in hrs for l in hl.get(h,[])]
    if vs: out.append(f"{name:>12}: {len(vs):>4}件  平均閲覧 {statistics.mean(vs):>7.0f}  平均いいね {statistics.mean(ls):>5.1f}")

res="\n".join(out)
open("yu_result.txt","w").write(res); print(res)
