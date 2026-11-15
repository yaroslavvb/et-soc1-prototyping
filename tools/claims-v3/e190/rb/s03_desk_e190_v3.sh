#!/usr/bin/env bash
# E190 (Q177, the kit's dated note 2, lane note2-e190, Sat 14 Nov 2026, after E190's first card day and before any later E190 day), the box
# step "step 2" v3 (this file is s03 v3): the desk check before any box step, on the desk only (aifoundry2). It is step 2 v2
# (rb/s03_desk_e190_v2.sh, note 1's, which stays as committed and runs unchanged inside it: the window, the pull under the lab-git lock, the
# registration, the kit and note 1 ancestors of HEAD, E190's paths clean, the history check, the three lists at their pinned counts and bytes,
# the harness v2, the self-checks, the forecast and plan re-made, the stub self-test, the preflight v2, note 1's desk tests' logs, HEAD
# unchanged across them) with note 2's checks after it, on the same HEAD. Note 2 replaces step 10 (rb/s20_wait_e190_v3.sh, in note 2's
# list), and step 2 v2 pins note 1's list, which names step 10 v2: so step 10 v3's bytes are gated here, never only reported.
#   1. RB_OUT and RB_LOCK set, RB_OUT outside the repo, and the window written today (as v2 refuses: 10, before any call);
#   2. step 2 v2, unchanged; its exit status stops this step (it reports note 2's list as one it does not pin: never a gate there);
#   3. NOTE 2'S COMMIT, found by its content (the commit that added tools/claims-v3/e190/KIT.md.dated-note-2.md), an ancestor of HEAD;
#   4. note 2's list, SHA256SUMS-e190-kit-note2, at its pinned count and its own pinned sha256 (NOTE2PIN below), every entry OK;
#   5. note 2's desk tests' logs as committed, each with its PASS line once, and the dry listing v3's last line;
#   6. HEAD unchanged from the HEAD step 2 v2's last line names to the end of 3-5, else 16 (a co-owner's commit meanwhile: run it again).
# This file is not in note 2's list (a file cannot hold its own list's sha256): the go's anchor lines give its sha256 beside the list's.
# Exit codes are k6's: 0 passed; 10 usage or order; 16 a gate says stop (the STOP line names why); v2's own codes pass through.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e190/rb/s03_desk_e190_v3.sh      (never inside the lab-git lock: v2 takes it itself)
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=${RB_REPO:-$(cd "$D/../../../.." && pwd)}
STEP=s03_desk_v3_e190
E=tools/claims-v3/e190
NOTE2PIN=tools/claims-v3/e190/SHA256SUMS-e190-kit-note2:8:58225c4f31ae7e275429b923a21a6f320b04eb3ed740e795e44590793fdd5f75   # note 2's own list, at its count and its own bytes (set at the note's commit)
LOGS="logs/selftest-wait-e190-v3.txt:^SELFTEST-WAIT-E190-V3.[0-9]+.of.[0-9]+.PASS$ logs/realread-wait-e190-v3.txt:^REALREAD-WAIT-E190-V3.[0-9]+.of.[0-9]+.PASS$ logs/dry-listing-e190-v3.txt:^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$"
say() { if [ -n "${RB_DRY:-}" ]; then echo "[$STEP] (dry listing; a real run would say:) $*"; else echo "[$STEP] $*"; fi; }
die() { local c=$1; shift; echo "[$STEP] STOP: $*"; echo "$(date '+%F %T %Z') step=$STEP exit=$c $*" >> "$RB_OUT/runbook.log"; exit "$c"; }
[ -n "${RB_OUT:-}" ] || { echo "[$STEP] RB_OUT is not set (this card day's own directory, outside the repo)"; exit 10; }
[ -n "${RB_LOCK:-}" ] || { echo "[$STEP] RB_LOCK is not set (the lock file a login check is appended to)"; exit 10; }
mkdir -p "$RB_OUT" || exit 10
o=$(cd "$RB_OUT" && pwd -P); r=$(cd "$REPO" && pwd -P)
case "$o/" in "$r/"*) echo "[$STEP] RB_OUT is inside the lab repo: refused"; exit 10 ;; esac
[ -n "${RB_DRY:-}" ] && echo "=== [$STEP] dry listing: nothing below is run"
if [ -z "${RB_DRY:-}" ]; then
  [ -f "$RB_OUT/window.env" ] || die 10 "no window in RB_OUT: run s02_window_e190.sh with his go's day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    die 10 "RB_OUT's window was not written today (Pacific): run s02_window_e190.sh with his go's day, last start and last end first"
fi
# 2. step 2 v2, unchanged (its output also kept in RB_OUT, to read the HEAD its checks ran on)
cap=$RB_OUT/s03-v2-in-v3-$$.txt
bash "$D/s03_desk_e190_v2.sh" | tee "$cap"
rc=${PIPESTATUS[0]}
if [ "$rc" -ne 0 ]; then
  echo "[$STEP] STOP: step 2 v2 exited $rc (its STOP line above names why)"
  echo "$(date '+%F %T %Z') step=$STEP exit=$rc step 2 v2 exited $rc" >> "$RB_OUT/runbook.log"
  exit "$rc"
fi
if [ -n "${RB_DRY:-}" ]; then
  say "note 2's checks on the same HEAD: note 2's commit (the commit that added $E/KIT.md.dated-note-2.md) an ancestor of HEAD; $(basename "${NOTE2PIN%%:*}") at its $(echo "$NOTE2PIN" | cut -d: -f2) entries, its own bytes and every entry OK (step 10 v3 among them); note 2's desk tests' logs as committed; HEAD unchanged from step 2 v2's reading"
  exit 0
fi
cd "$REPO" || die 10 "no repository at $REPO"
hv2=$(sed -nE 's/^\[s03_desk_v2_e190\] desk check v2: .* HEAD ([0-9a-f]{12}) descends from .*$/\1/p' "$cap" | tail -n 1)
h1=$(git rev-parse HEAD 2>/dev/null)
[ -n "$hv2" ] || die 16 "step 2 v2 passed but its last line names no HEAD: read its output above"
[ "${h1:0:12}" = "$hv2" ] || die 16 "HEAD-moved: step 2 v2 checked $hv2, HEAD is now ${h1:0:12} (a co-owner's commit meanwhile): run step 2 v3 again"
bad=""
# 3. note 2's commit, by its content
note2=$(git log --diff-filter=A --format=%H -- "$E/KIT.md.dated-note-2.md" 2>/dev/null | tail -n 1)
if [ -z "$note2" ]; then bad="$bad note2(missing)"
elif ! git merge-base --is-ancestor "$note2" HEAD 2>/dev/null; then bad="$bad note2-ancestry"; fi
# 4. note 2's list, at its pinned count and its own pinned bytes, every entry OK
l=${NOTE2PIN%%:*}; pin=$(echo "$NOTE2PIN" | cut -d: -f2); hpin=$(echo "$NOTE2PIN" | cut -d: -f3)
if [ -f "$l" ]; then
  n=$(grep -c . "$l"); own=$(sha256sum "$l" | cut -d' ' -f1); okn=$(sha256sum -c "$l" 2>/dev/null | grep -c ': OK$')
  why=""; [ "$own" = "$hpin" ] || why="; its own bytes differ from the pin"
  { [ "$n" = "$pin" ] && [ "$okn" = "$n" ] && [ -z "$why" ]; } || bad="$bad $(basename "$l")($okn OK of $n; pinned $pin$why)"
else
  bad="$bad $(basename "$l")(missing)"
fi
# 5. note 2's desk tests' logs, as committed
for spec in $LOGS; do
  lf=${spec%%:*}; pat=${spec#*:}
  [ "$(grep -cE "$pat" "$E/$lf" 2>/dev/null)" = 1 ] || bad="$bad $(basename "$lf" .txt)"
done
# 6. the tree did not move
h2=$(git rev-parse HEAD 2>/dev/null)
[ "$h1" = "$h2" ] || die 16 "HEAD-moved: the lab clone moved during note 2's checks (${h1:0:12} to ${h2:0:12}): run step 2 v3 again"
[ -z "$bad" ] || die 16 "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$STEP desk check v3 passed at $h1 (note 2 $note2)" >> "$RB_OUT/runbook.log"
say "desk check v3: step 2 v2 passed at HEAD ${h1:0:12}; then on the same HEAD note 2 ${note2:0:12} an ancestor, note 2's list at its $pin entries, its own bytes and every entry OK (step 10 v3 among them), note 2's desk tests' logs as committed"
