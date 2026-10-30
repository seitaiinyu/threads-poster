#!/bin/bash
# 昼〜夕方に起動し、JST 23:45 まで15分おきに auto_post.py を回す。
# 19時前は auto_post.py 側が「夜枠はまだ」と判断して何も出さないので、早く起動しても害はない。
# GitHubの1ジョブ上限(6h)に当たりそうなら、自分自身を再起動して23:45まで引き継ぐ。
START=$(date +%s)
while true; do
  H=$(TZ=Asia/Tokyo date +%H); M=$(TZ=Asia/Tokyo date +%M)
  NOW=$((10#$H*60 + 10#$M))
  ELAPSED=$(( ($(date +%s) - START) / 60 ))
  if [ $NOW -ge $((23*60+45)) ] || [ $NOW -lt $((11*60)) ]; then
    echo "終了 (JST ${H}:${M}, 経過${ELAPSED}分)"; break
  fi
  if [ $ELAPSED -ge 330 ]; then
    echo "上限が近いので引き継ぎ起動 (JST ${H}:${M})"
    gh workflow run evening_yu.yml || echo "引き継ぎ起動に失敗"
    break
  fi
  echo "=== JST ${H}:${M} ==="
  BATCH=2 python3 auto_post.py || echo "今回は失敗、次回に再試行"
  sleep 900
done
