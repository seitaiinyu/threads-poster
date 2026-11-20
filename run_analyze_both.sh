#!/bin/bash
# 両アカウントの14日分析を順に実行して結果ファイルへ出力
cd "$(dirname "$0")"
OUT="${1:-/tmp/analyze_both.txt}"
set -a; source .env; set +a
LABEL="①ダイエット" python3 analyze14.py > "$OUT" 2>&1
set -a; source .env.yu; set +a
LABEL="②整体" python3 analyze14.py >> "$OUT" 2>&1
echo "DONE" >> "$OUT"
