#!/usr/bin/env bash
# deploy_all.sh [--dry] : for each page, check the live copy is still the pre-review version, then deploy the repo copy.
cd /home/yaroslavvb/claude/et-soc1-prototyping
A=${AUDIT_DIR:-/tmp/report-review}
SS="/home/yaroslavvb/.local/node/bin/node /home/yaroslavvb/.local/lib/node_modules/spacesheep/bin/spacesheep.js"
BASE=${BASE:-08076ae}   # the tree the review started from (d04b29a on 24 Sep, 08076ae on 25 Sep)
DRY=$1
norm() { sed -E 's/ data-ss-id="[^"]*"//g' "$1" | sed -e '$a\'; }
while IFS=$'\t' read slug uuid html; do
  [ "$slug" = david-kanter-power-brief ] && continue
  now=$(mktemp -d); timeout 180 $SS read $uuid index.html 2>/dev/null | sed '1{/^--- index.html/d}' > $now/live.html
  if git cat-file -e $BASE:$html 2>/dev/null; then git show $BASE:$html > $now/base.html; else cp $A/live/$slug/index.html $now/base.html; fi
  if cmp -s <(norm $now/live.html) <(norm $now/base.html); then st="live=pre-review"; else st="LIVE CHANGED SINCE REVIEW"; fi
  title=$(python3 -c "import re,html,sys;s=open(sys.argv[1]).read();m=re.search(r'<title>(.*?)</title>',s,re.S);print(html.unescape(m.group(1)).strip() if m else '')" "$html")
  echo "$slug | $st | title: $title"
  if [ "$st" != "live=pre-review" ] || [ -n "$DRY" ]; then rm -rf $now; continue; fi
  D=$A/deploy/$slug; rm -rf $D; mkdir -p $D; cp "$html" $D/index.html
  [ "$slug" = et-soc1-horace-experiment ] && cp docs/reports/horace-heating.gif docs/reports/horace-heating-6.gif docs/reports/horace-long.gif $D/
  # --slug with --title: a title alone re-slugs the space and breaks its URL (24 Sep 2026)
  $SS deploy $D --space $uuid --slug "$slug" --title "$title" -m "${MSG:-Report review: claims checked against the data, cross-links, readability}" --json 2>&1 | grep -E '"(is_update|visibility)"' | head -2 | tr -d '\n '; echo
  rm -f $D/.spacesheep.json; rm -rf $now
done < <(tail -n +2 $A/manifest.tsv | awk -F'\t' 'BEGIN{OFS="\t"} {h=$3; if($1=="et-soc1-spatial-temperature-brief") h="docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html"; if($1=="2026-09-22-et-soc1-l2-mainline-starvation") h="docs/reports/2026-09-22-et-soc1-l2-mainline-starvation.html"; print $1,$2,h}')
