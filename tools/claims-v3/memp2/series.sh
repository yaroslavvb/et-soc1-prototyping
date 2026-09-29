#!/usr/bin/env bash
# memp2: several blocks in a row on this host's card, in place of queue.sh. queue.sh reads the die before every block
# through lib's die_c, which opens the card's management node outside the card lock, before any et-who check and
# under a 20 s cap; here each block does all of its own checks (et-who --check, others_present, ours_running, the
# card lock, the start temperature read under the lock with timeout 10) and this script only runs them in order.
#
#   V3_DEVICE=1 bash tools/claims-v3/memp2/series.sh 901 101 201 102 202                     aifoundry1 card 1
#   MEMP2_LOCK_SHA256=<sha> bash tools/claims-v3/memp2/series.sh 911 111 211 112 212         aifoundry3
#
# A pass whose block.json says ok ends at once (block_begin: "already done"). The series stops at the first block
# that does not exit 0 (a failure, a refusal, or someone else on the card: the operator decides what next) and
# before any block while the STOP file exists. MEMP2_GAP seconds (default 20) between blocks. V3_DRY=1 passes
# through. Start it detached (README.md, "How to run").
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
[ $# -ge 1 ] || { echo "usage: series.sh <pass> ..." >&2; exit 2; }
for p in "$@"; do case "$p" in ''|*[!0-9]*) echo "series.sh: bad pass '$p'" >&2; exit 2 ;; esac; done
STOPFILE=build/claims-v3/STOP; [ -n "${V3_DRY:-}" ] && STOPFILE=build/claims-v3-dry/STOP
gap=${MEMP2_GAP:-20}
first=1
for p in "$@"; do
  [ -z "$first" ] && { [ -n "${V3_DRY:-}" ] || sleep "$gap"; }
  first=
  [ -e "$STOPFILE" ] && { echo "$(date +%FT%T) series: $STOPFILE present: stopping before memp2 $p"; exit 1; }
  echo "$(date +%FT%T) series: memp2 $p"
  bash tools/claims-v3/memp2/block.sh "$p" < /dev/null; rc=$?
  echo "$(date +%FT%T) series: memp2 $p exit $rc"
  [ $rc -eq 0 ] || { echo "$(date +%FT%T) series: stopping after memp2 $p (exit $rc)"; exit $rc; }
done
echo "$(date +%FT%T) series: done ($*)"
