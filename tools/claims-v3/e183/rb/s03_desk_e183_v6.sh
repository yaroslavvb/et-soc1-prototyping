#!/usr/bin/env bash
# E183 (the kit's dated note 5, KIT.md.dated-note-5.md, Fri 13 Nov 2026, before any E183 datum): KIT.md box step 2 v6, the desk check before
# any box step, on the desk the card lane orchestrates from (the Intel, or aifoundry2 since Fri 13 Nov 2026). It is step 2 v5
# (s03_desk_e183_v5.sh, 24b9b99e, which stays as committed and runs unchanged inside it: step 2 v4, then note 4's lists, harness and logs)
# with note 5's checks after it, on the same HEAD:
#   1. RB_OUT and RB_LOCK set, RB_OUT outside the repo, and the window written today (as v5 refuses: 10, before any call);
#   2. step 2 v5, unchanged; its exit status stops this step (it reports note 5's list as one it does not know: never a gate there);
#   3. note 5's list, SHA256SUMS-e183-kit-note5, at its pinned count and its own pinned sha256, with every entry OK: a gate (16);
#   4. note 5's two desk tests' logs as committed (SELFTEST-NOPATH-E183 PASS, SELFTEST-COLLECT-E183-V3 ... PASS);
#   5. HEAD unchanged across 3-4, else 16.
# This file is not in note 5's list (a file cannot hold its own list's sha256): the go's anchor lines give its sha256 beside the list's.
# Revised before the land by the lane fix-note5 of Q170 (after the verifier verify-note5): the list's pinned count (24, was 22) and its own
# pinned sha256; nothing else.
# Exit codes are k6's: 0 passed; 10 usage or order; 16 a gate says stop (the STOP line names why); v5's own codes pass through.
#   bash tools/claims-v3/e183/rb/s03_desk_e183_v6.sh
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=${RB_REPO:-$(cd "$D/../../../.." && pwd)}
STEP=s03_desk_v6_e183
E=tools/claims-v3/e183
NOTE5_LIST=SHA256SUMS-e183-kit-note5
NOTE5_N=24
NOTE5_SHA=5f27fd32d41b8db9618680d18e92375bd254e3f89e95f84e10514ef9ab5a0c8e
LOGS="logs/selftest-nopath-e183.txt:^SELFTEST-NOPATH-E183.PASS logs/selftest-collect-e183-v3.txt:^SELFTEST-COLLECT-E183-V3.[0-9]+.of.[0-9]+.PASS"
say() { if [ -n "${RB_DRY:-}" ]; then echo "[$STEP] (dry listing; a real run would say:) $*"; else echo "[$STEP] $*"; fi; }
die() { local c=$1; shift; echo "[$STEP] STOP: $*"; echo "$(date '+%F %T %Z') step=$STEP exit=$c $*" >> "$RB_OUT/runbook.log"; exit "$c"; }
[ -n "${RB_OUT:-}" ] || { echo "[$STEP] RB_OUT is not set (this card day's own directory, outside the repo)"; exit 10; }
[ -n "${RB_LOCK:-}" ] || { echo "[$STEP] RB_LOCK is not set (the lock file a login check is appended to)"; exit 10; }
mkdir -p "$RB_OUT" || exit 10
o=$(cd "$RB_OUT" && pwd -P); r=$(cd "$REPO" && pwd -P)
case "$o/" in "$r/"*) echo "[$STEP] RB_OUT is inside the lab repo: refused"; exit 10 ;; esac
[ -n "${RB_DRY:-}" ] && echo "=== [$STEP] dry listing: nothing below is run"
if [ -z "${RB_DRY:-}" ]; then
  [ -f "$RB_OUT/window.env" ] || die 10 "no window in RB_OUT: run s02_window_e183.sh first (kit v5: s02 before s03)"
  [ "$(date -r "$RB_OUT/window.env" +%F)" = "$(date +%F)" ] || die 10 "RB_OUT's window was not written today: run s02_window_e183.sh first"
fi
# 2. step 2 v5, unchanged
bash "$D/s03_desk_e183_v5.sh"
rc=$?
[ "$rc" -eq 0 ] || { echo "[$STEP] STOP: step 2 v5 exited $rc (its STOP line above names why)"; exit "$rc"; }
if [ -n "${RB_DRY:-}" ]; then
  say "note 5's checks on the same HEAD: $NOTE5_LIST at its $NOTE5_N entries, its own bytes and every entry OK; note 5's two desk tests' logs"
  exit 0
fi
cd "$REPO" || die 10 "no repository at $REPO"
h1=$(git rev-parse HEAD 2>/dev/null)
bad=""
# 3. note 5's list
p=$E/$NOTE5_LIST
if [ -f "$p" ]; then
  n=$(grep -c . "$p"); own=$(shasum -a 256 "$p" | cut -d' ' -f1); okn=$(shasum -a 256 -c "$p" 2>/dev/null | grep -c ': OK$')
  { [ "$n" -eq "$NOTE5_N" ] && [ "$own" = "$NOTE5_SHA" ] && [ "$okn" -eq "$n" ]; } || bad="$bad $NOTE5_LIST($okn OK of $n; pinned $NOTE5_N and its own bytes, own ${own:0:12})"
else
  bad="$bad $NOTE5_LIST(missing)"
fi
# 4. note 5's desk tests' logs
for spec in $LOGS; do
  lf=${spec%%:*}; pat=${spec#*:}
  [ "$(grep -cE "$pat" "$E/$lf" 2>/dev/null)" = 1 ] || bad="$bad $(basename "$lf" .txt)"
done
# 5. the tree did not move
h2=$(git rev-parse HEAD 2>/dev/null)
[ -n "$h1" ] && [ "$h1" = "$h2" ] || die 16 "the lab clone moved during note 5's checks (${h1:0:12} to ${h2:0:12}): run step 2 v6 again"
[ -z "$bad" ] || die 16 "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$STEP desk check v6 passed at $h1" >> "$RB_OUT/runbook.log"
say "desk check v6: step 2 v5 passed, then on the same HEAD ${h1:0:12} note 5's list at its $NOTE5_N entries, its own bytes and every entry OK, and note 5's two desk tests' logs as committed"
