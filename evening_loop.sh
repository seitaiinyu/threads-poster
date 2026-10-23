#!/bin/bash
# 夕方に1回起動し、JST 23:45 まで15分おきに auto_post.py を回す。
# GitHubの定時実行が19〜23時に間引かれても、この1本が動けば夜枠が埋まる。
START=$(date +%s)
while true; do
  H=$(TZ=Asia/Tokyo date +%H); M=$(TZ=Asia/Tokyo date +%M)
  NOW=$((10#$H*60 + 10#$M))
  ELAPSED=$(( ($(date +%s) - START) / 60 ))
  if [ $NOW -ge $((23*60+45)) ] || [ $NOW -lt $((12*60)) ] || [ $ELAPSED -ge 345 ]; then
    echo "終了 (JST ${H}:${M}, 経過${ELAPSED}分)"; break
  fi
  echo "=== JST ${H}:${M} ==="
  BATCH=2 python3 auto_post.py || echo "今回は失敗、次回に再試行"
  sleep 900
done
