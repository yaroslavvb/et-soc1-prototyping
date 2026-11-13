#!/usr/bin/env bash
# E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): KIT.md box step 2 v7, the desk check
# before any box step of E183's second session that day (E183.md's dated amendment A1). It is step 2 v6 (s03_desk_e183_v6.sh, 9ae55d39,
# which stays as committed and runs unchanged inside it: step 2 v5, then note 5's list and logs) with note 6's checks after it, on the
# same HEAD:
#   1. RB_OUT and RB_LOCK set, RB_OUT outside the repo, and the window written today (as v6 refuses: 10, before any call);
#   2. step 2 v6, unchanged; its exit status stops this step (step 2 v5 inside it reports note 6's and A1's lists as lists it does not
#      know: never a gate there);
#   3. note 6's list, SHA256SUMS-e183-kit-note6, and amendment A1's list, SHA256SUMS-e183-a1, each at its pinned count and its own pinned
#      sha256, with every entry OK: a gate (16);
#   4. the harness v3: make_harness_e183_v3.py --check (CHECK PASS: harness-e183-v3.json is the committed files' own) and
#      harness_e183_v3.py (HARNESS OK: v2's check, then note 6's five box files at their pins), a gate (16);
#   5. note 6's four desk tests' logs as committed (DESKTEST-REALPATH-E183 PASS, SELFTEST-WAIT-E183 PASS, SELFTEST-ASIDE-E183 PASS, and
#      SELFTEST-RB-E183-V4 PASS, whose case L runs step 9 v3's launch path: added before the land by the lane fix-n6, for verify-n6's
#      finding 1);
#   6. HEAD unchanged across 3-5, else 16.
# This file is in neither list (a file cannot hold the sha256 of a list that holds its own): the go's anchor lines give its sha256 beside
# the lists'. Exit codes are k6's: 0 passed; 10 usage or order; 16 a gate says stop (the STOP line names why); v6's own codes pass through.
#   bash tools/claims-v3/e183/rb/s03_desk_e183_v7.sh
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=${RB_REPO:-$(cd "$D/../../../.." && pwd)}
STEP=s03_desk_v7_e183
E=tools/claims-v3/e183
NOTE6_N=47
NOTE6_SHA=029f7b5130b0afb7d296cf65cf7d184c6f62bf2dd7764ae8c05ff73a85e53f0e
A1_N=5
A1_SHA=60490d00066e51a11aa8bd155574f9583c93896e13578433bca4367f2ad38c06
LOGS="logs/desktest-realpath-e183.txt:^DESKTEST-REALPATH-E183.PASS logs/selftest-wait-e183.txt:^SELFTEST-WAIT-E183.PASS logs/selftest-aside-e183.txt:^SELFTEST-ASIDE-E183.PASS logs/selftest-rb-e183-v4.txt:^SELFTEST-RB-E183-V4.PASS"
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
# 2. step 2 v6, unchanged
bash "$D/s03_desk_e183_v6.sh"
rc=$?
[ "$rc" -eq 0 ] || { echo "[$STEP] STOP: step 2 v6 exited $rc (its STOP line above names why)"; exit "$rc"; }
if [ -n "${RB_DRY:-}" ]; then
  say "note 6's checks on the same HEAD: SHA256SUMS-e183-kit-note6 at its $NOTE6_N entries and SHA256SUMS-e183-a1 at its $A1_N, each at its own bytes with every entry OK; the harness v3 (CHECK PASS, HARNESS OK); note 6's four desk tests' logs"
  exit 0
fi
cd "$REPO" || die 10 "no repository at $REPO"
h1=$(git rev-parse HEAD 2>/dev/null)
bad=""
# 3. note 6's list and amendment A1's list
for spec in "SHA256SUMS-e183-kit-note6 $NOTE6_N $NOTE6_SHA" "SHA256SUMS-e183-a1 $A1_N $A1_SHA"; do
  set -- $spec; l=$1; want_n=$2; want_sha=$3
  p=$E/$l
  if [ -f "$p" ]; then
    n=$(grep -c . "$p"); own=$(shasum -a 256 "$p" | cut -d' ' -f1); okn=$(shasum -a 256 -c "$p" 2>/dev/null | grep -c ': OK$')
    { [ "$n" -eq "$want_n" ] && [ "$own" = "$want_sha" ] && [ "$okn" -eq "$n" ]; } || bad="$bad $l($okn OK of $n; pinned $want_n and its own bytes, own ${own:0:12})"
  else
    bad="$bad $l(missing)"
  fi
done
# 4. the harness v3
mk=$(/usr/bin/python3 -B "$E/make_harness_e183_v3.py" --check 2>&1 | tail -n 1)
[ "$mk" = "CHECK PASS" ] || bad="$bad make_harness_e183_v3.py --check($mk)"
hv=$(/usr/bin/python3 -B "$E/harness_e183_v3.py" 2>&1 | tail -n 1)
case "$hv" in "HARNESS OK: "*) ;; *) bad="$bad harness_e183_v3.py(${hv:0:160})" ;; esac
# 5. note 6's desk tests' logs
for spec in $LOGS; do
  lf=${spec%%:*}; pat=${spec#*:}
  [ "$(grep -cE "$pat" "$E/$lf" 2>/dev/null)" = 1 ] || bad="$bad $(basename "$lf" .txt)"
done
# 6. the tree did not move
h2=$(git rev-parse HEAD 2>/dev/null)
[ -n "$h1" ] && [ "$h1" = "$h2" ] || die 16 "the lab clone moved during note 6's checks (${h1:0:12} to ${h2:0:12}): run step 2 v7 again"
[ -z "$bad" ] || die 16 "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$STEP desk check v7 passed at $h1" >> "$RB_OUT/runbook.log"
say "desk check v7: step 2 v6 passed, then on the same HEAD ${h1:0:12} note 6's list at its $NOTE6_N entries and amendment A1's at its $A1_N, each at its own bytes with every entry OK; the harness v3 ($hv); note 6's four desk tests' logs as committed"
