#!/bin/sh
sleep 5
while true; do
  BUCKETS=$(aws s3api list-buckets \
    --query 'Buckets[].{Name:Name,Date:CreationDate}' \
    --output json 2>/dev/null)
  COUNT=$(echo "$BUCKETS" | python3 -c "import sys,json;print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
  ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "N/A")
  NOW=$(date -u "+%Y-%m-%d %H:%M UTC")
  python3 /scripts/render.py "$ACCOUNT" "$COUNT" "$NOW" "$BUCKETS"
  sleep 30
done
