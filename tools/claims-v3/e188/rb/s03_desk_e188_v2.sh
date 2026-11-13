#!/usr/bin/env bash
# E188 (Q165, the kit's dated note 1, KIT.md.dated-note-1.md, Thu 12 Nov 2026, before any E188 datum): KIT.md box step 2 v2, the desk check
# before any box step, on the Intel only. It is step 2 v1 (rb/s03_desk_e188.sh, 726a6b64, which stays as committed and runs unchanged inside
# it: the window written today for E188, the pull under the lab-git lock, the ancestry, the paths clean, the history check, every list E188
# reads at its pins and the kit's own at 106 and its bytes, the harness, the items, the build inputs, the plan, the forecast, the statistics
# and the kit's desk tests' logs) with note 1's checks after it, on the same tree, in E183's step 2 v5 form:
#   1. RB_OUT and RB_LOCK set, RB_OUT outside the repo, and the window written today (Pacific), as v1 refuses (10), before any call;
#   2. step 2 v1, unchanged; its exit status stops this step;
#   3. note 1's two lists, each at its pinned count, its own pinned sha256 and every entry OK (a gate): the registration's dated amendment A1
#      and dated note 1 (SHA256SUMS-e188-a1) and the kit's dated note 1 (SHA256SUMS-e188-kit-note1: the rest rule v2, step 9 v2, the dry
#      listing v2, their desk tests, the notes and their logs). A changed, short or missing list stops the step (16). v1 reports both lists
#      as lists it does not pin, never as a gate; this step pins them;
#   4. note 1's desk tests' logs as committed, each with its PASS line once: the rest rule v2's (SELFTEST-REST-E188-V2), the runbook's v2
#      (SELFTEST-RB-E188-V2) and the dry listing v2's last line (19 steps, 0 exiting non-zero);
#   5. HEAD unchanged across 3-4, else 16.
# This file is not in note 1's list (a file cannot hold its own list's sha256): E188's anchor lines give its sha256 beside the list's.
# Exit codes are k6's: 0 passed; 10 usage or order; 16 a gate says stop (the STOP line names why); v1's own codes pass through.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e188/rb/s03_desk_e188_v2.sh
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=${RB_REPO:-$(cd "$D/../../../.." && pwd)}
STEP=s03_desk_v2_e188
E=tools/claims-v3/e188
# name:count:its own sha256 (each a gate: count, bytes and every entry)
A1_PIN=SHA256SUMS-e188-a1:2:63f7076376bbd13e5394bfc8c94cbf4905de8968851e9158e1a7ba34c982a4a2
N1_PIN=SHA256SUMS-e188-kit-note1:10:994e8e92f9ef22df65630ee8e108a9bb53a55a18a633c1e6f654029bd7b3a3c2
NOTE1_LISTS="$A1_PIN
$N1_PIN"
LOGS="logs/selftest-rest-e188-v2.txt:^SELFTEST-REST-E188-V2.PASS logs/selftest-rb-e188-v2.txt:^SELFTEST-RB-E188-V2.[0-9]+.of.[0-9]+.PASS
logs/dry-listing-e188-v2.txt:^dry.listing:.19.steps.listed,.0.exited.non-zero$"
say() { if [ -n "${RB_DRY:-}" ]; then echo "[$STEP] (dry listing; a real run would say:) $*"; else echo "[$STEP] $*"; fi; }
die() { local c=$1; shift; echo "[$STEP] STOP: $*"; echo "$(date '+%F %T %Z') step=$STEP exit=$c $*" >> "$RB_OUT/runbook.log"; exit "$c"; }
# 1. as v1 refuses, before any call
[ -n "${RB_OUT:-}" ] || { echo "[$STEP] RB_OUT is not set (this card day's own directory, outside the repo)"; exit 10; }
[ -n "${RB_LOCK:-}" ] || { echo "[$STEP] RB_LOCK is not set (the lock file a login check is appended to)"; exit 10; }
mkdir -p "$RB_OUT" || exit 10
o=$(cd "$RB_OUT" && pwd -P); r=$(cd "$REPO" && pwd -P)
case "$o/" in "$r/"*) echo "[$STEP] RB_OUT is inside the lab repo: refused"; exit 10 ;; esac
[ -n "${RB_DRY:-}" ] && echo "=== [$STEP] dry listing: nothing below is run"
if [ -z "${RB_DRY:-}" ]; then
  [ -f "$RB_OUT/window.env" ] || die 10 "no window in RB_OUT: run s02_window_e188.sh with his go's day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    die 10 "RB_OUT's window was not written today (Pacific): run s02_window_e188.sh first"
fi
# 2. step 2 v1, unchanged
bash "$D/s03_desk_e188.sh"
rc=$?
[ "$rc" -eq 0 ] || { echo "[$STEP] STOP: step 2 v1 exited $rc (its STOP line above names why)"; exit "$rc"; }
if [ -n "${RB_DRY:-}" ]; then
  say "note 1's checks on the same HEAD: its two lists (the registration's dated amendment A1 and note 1's, and the kit's dated note 1's) each at its pinned count, its own bytes and every entry; the rest rule v2's, the runbook v2's and the dry listing v2's logs as committed; HEAD unchanged"
  exit 0
fi
cd "$REPO" || die 10 "no repository at $REPO"
h1=$(git rev-parse HEAD 2>/dev/null)
bad=""
# 3. note 1's two lists
while IFS=: read -r name pin psha; do
  [ -n "$name" ] || continue
  p=$E/$name
  [ -f "$p" ] || { bad="$bad $name(missing)"; continue; }
  n=$(grep -c . "$p"); own=$(shasum -a 256 "$p" | cut -d' ' -f1); okn=$(shasum -a 256 -c "$p" 2>/dev/null | grep -c ': OK$')
  { [ "$n" -eq "$pin" ] && [ "$own" = "$psha" ] && [ "$okn" -eq "$n" ]; } || bad="$bad $name($okn OK of $n; pinned $pin and its own bytes${own:+, own ${own:0:12}})"
done <<EOF2
$NOTE1_LISTS
EOF2
# 4. note 1's desk tests' logs, as committed
for spec in $LOGS; do
  lf=${spec%%:*}; pat=${spec#*:}
  [ "$(grep -cE "$pat" "$E/$lf" 2>/dev/null)" = 1 ] || bad="$bad $(basename "$lf" .txt)"
done
# 5. the tree did not move
h2=$(git rev-parse HEAD 2>/dev/null)
[ -n "$h1" ] && [ "$h1" = "$h2" ] || die 16 "the lab clone moved during note 1's checks (${h1:0:12} to ${h2:0:12}): run step 2 v2 again"
[ -z "$bad" ] || die 16 "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$STEP desk check v2 passed at $h1" >> "$RB_OUT/runbook.log"
say "desk check v2: step 2 v1 passed, then on the same HEAD ${h1:0:12} note 1's two lists at their pinned counts, own bytes and entries (SHA256SUMS-e188-a1 $(echo "$NOTE1_LISTS" | sed -n 1p | cut -d: -f2), SHA256SUMS-e188-kit-note1 $(echo "$NOTE1_LISTS" | sed -n 2p | cut -d: -f2)); the rest rule v2's, the runbook v2's and the dry listing v2's logs as committed"
