#!/bin/bash
# postfix.sh : after the fixers: rebuild both pages through the whole chain, re-check the line citations, crawl the
# rebuilt chip diagram (served on 127.0.0.1:8918 from serve/, which links the repo's built pages) and diff what a reader
# sees against the morning's crawl. Logs to the work dir; stops at the first failing build step.
set -euo pipefail
W=/home/yaroslavvb/claude/work/chip-check-1014
R=/home/yaroslavvb/claude/et-soc1-prototyping
bash $W/buildchain.sh $R > $W/postfix-build.log 2>&1 || { echo "BUILD FAILED"; tail -40 $W/postfix-build.log; exit 1; }
tail -8 $W/postfix-build.log
python3 -I $W/citecheck.py $R --out $W/cites-after.json --md $W/cites-after.md | tail -1
cd $W/crawl
rm -rf "${W:?}/crawl/after"
timeout 2400 node crawl.mjs http://127.0.0.1:8918/chip.html $W/crawl/after > $W/crawl/after.log 2>&1 || { echo "CRAWL FAILED"; tail -20 $W/crawl/after.log; exit 1; }
tail -3 $W/crawl/after.log
python3 -I $W/crawldiff.py $W/crawl/out $W/crawl/after $W/crawl-diff.md
