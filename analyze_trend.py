#!/usr/bin/env python3
"""アカウント1の閲覧数を時系列（週・日単位）で分析し、リーチ低下の時期と傾向を特定。"""
import os, json, time, urllib.request, urllib.parse, statistics
from datetime import datetime, timezone, timedelta
from collections import defaultdict

API="https://graph.threads.net/v1.0"
DIR=os.path.dirname(os.path.abspath(__file__))
JST=timezone(timedelta(hours=9))
TOK=os.environ["THREADS_ACCESS_TOKEN"]

posts=json.load(open(os.path.join(DIR,"posts_90d.json")))
posts=[p for p in posts if p.get("media_type") in ("TEXT_POST","IMAGE")]
# 日付ごとの投稿数（全件＝投稿量の推移）
vol=defaultdict(int)
for p in posts:
    d=datetime.strptime(p["timestamp"],"%Y-%m-%dT%H:%M:%S%z").astimezone(JST).strftime("%Y-%m-%d")
    vol[d]+=1

# 閲覧数サンプリング（~600件、全期間に均等）
step=max(1,len(posts)//600)
sample=posts[::step]

def views(mid):
    url=f"{API}/{mid}/insights?metric=views&access_token="+urllib.parse.quote(TOK)
    try:
        with urllib.request.urlopen(url) as r: d=json.loads(r.read().decode())
        for m in d.get("data",[]):
            if m["name"]=="views":
                v=m.get("values",[{}]); return v[0].get("value",0) if v else 0
    except Exception: return None
    return 0

rows=[]
log=open(os.path.join(DIR,"trend_progress.txt"),"w")
for i,p in enumerate(sample,1):
    v=views(p["id"])
    if v is not None:
        dt=datetime.strptime(p["timestamp"],"%Y-%m-%dT%H:%M:%S%z").astimezone(JST)
        rows.append((dt,v))
    if i%100==0: log.write(f"{i}/{len(sample)}\n"); log.flush()
    time.sleep(0.03)

# 週(月曜起点)ごとに集計
def weekkey(dt):
    monday=dt-timedelta(days=dt.weekday())
    return monday.strftime("%m/%d週")
wk_views=defaultdict(list); wk_dates=defaultdict(list)
for dt,v in rows:
    wk_views[weekkey(dt)].append(v)

out=[]
out.append("===== アカウント1 リーチ推移（週別・JST）=====")
out.append(f"サンプル {len(rows)}件 / 母集団 {len(posts)}件\n")
out.append(f"{'週':>10} | {'投稿数':>5} | {'平均閲覧':>8} | {'中央値':>7} | {'最大':>7}")
# 投稿量も週集計
wk_vol=defaultdict(int)
for d,c in vol.items():
    dt=datetime.strptime(d,"%Y-%m-%d").replace(tzinfo=JST)
    wk_vol[weekkey(dt)]+=c
for wk in sorted(wk_views.keys()):
    vs=wk_views[wk]
    out.append(f"{wk:>10} | {wk_vol.get(wk,0):>5} | {statistics.mean(vs):>8.0f} | {statistics.median(vs):>7.0f} | {max(vs):>7}")

res="\n".join(out)
open(os.path.join(DIR,"trend_result.txt"),"w").write(res)
print(res)
