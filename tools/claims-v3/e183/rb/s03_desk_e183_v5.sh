#!/usr/bin/env bash
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): KIT.md box step 2 v5, the desk check before
# any box step, on the Intel only. It is step 2 v4 (s03_desk_e183_v4.sh, e8e9f4e1, which stays as committed and runs unchanged inside it:
# the day-2 check v2 with its own pull, then step 2 v3, the check v1 and step 2 v2) with note 4's checks after it, on the same tree:
#   1. RB_OUT and RB_LOCK set, RB_OUT outside the repo, and the window written today (as v4 refuses: 10, before any call);
#   2. step 2 v4, unchanged; its exit status stops this step;
#   3. E183's hash lists, found by "SHA256SUMS" ANYWHERE in a file's name under tools/claims-v3/e183 (the owed item of the records: a
#      perimeter that matched the name's start alone missed lists): the nine lists this step knows, each at its pinned count and its own
#      pinned sha256 -- the registration's 20, the kit's 46, note 1's 46, kit notes 2's 15, 3's 19 and 4's (THIS NOTE'S LIST), each with
#      every entry OK, a gate; the brief's 15, its count and bytes a gate (its entries the day-2 check reads, by its roles); notes M1's 25 and
#      M2's 9, reported, never a gate (october-forecast-model's arms are reported arms: their files cannot stop E183). A changed, short or
#      missing gate list stops the step (16); a list this step does not know is reported, never a gate (it gates no file E183 runs);
#   4. harness-e183-v2.json re-made (make_harness_e183_v2.py --check: CHECK PASS), harness_e183_v2.py without binaries (HARNESS OK: 87
#      files: v1's 80 and note 4's 7 box files), and note 4's four desk tests' logs as committed;
#   5. HEAD unchanged across 3-4, else 16.
# This file is not in note 4's list (a file cannot hold its own list's sha256): the anchor lines of E183's next day give its sha256 beside
# the list's. Exit codes are k6's: 0 passed; 10 usage or order; 16 a gate says stop (the STOP line names why); v4's own codes pass through.
#   bash tools/claims-v3/e183/rb/s03_desk_e183_v5.sh
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=${RB_REPO:-$(cd "$D/../../../.." && pwd)}
PY=${RB_PY:-/usr/bin/python3}
STEP=s03_desk_v5_e183
E=tools/claims-v3/e183
NOTE4_LIST=SHA256SUMS-e183-kit-note4
NOTE4_N=44
NOTE4_SHA=a10782bd39462081319db91fd9fb2e9cb597ea56adc6d5fe2752c85069077c64
# name:count:own sha256:role (gate: count, bytes and every entry; bytes: count and bytes; reported: printed, never a gate)
KNOWN="SHA256SUMS-e183-registration:20:6defebd4c3ec66a6e4b1b3e921751d0513a0c78d3869cffe489f2f43508a1a8a:gate
SHA256SUMS-e183-kit:46:2e06e0cc48bcf2fab2dc432e905a45456b35f058fab4603dcd732e9869bd8723:gate
SHA256SUMS-e183-note1:46:24d0c583cdf8678dd254ad3b87c613fb6735d26a21eafb034843600fdb5383e7:gate
SHA256SUMS-e183-kit-note2:15:6ebc97dbcf3923398451741936d31d7d4ffbdaf6928ba097a1aa3c370412c9cd:gate
SHA256SUMS-e183-kit-note3:19:3b472e387e24dd41eff814a60b6dd5da0ad11daeea147c8a4b76f30bf3515c22:gate
$NOTE4_LIST:$NOTE4_N:$NOTE4_SHA:gate
SHA256SUMS-e183-brief:15:02c8b2b62d2b9469cb4e67736393a3c3d2d1516c3b44b504742eb47e2c89cf10:bytes
SHA256SUMS-e183-m1:25:c8bad97187caf6f31c9e21ddae39fa7f4888f6a43f02962045b2cb24b3d34865:reported
SHA256SUMS-e183-m2:9:ced9afe24c6160fd966a949527298898e0d5c273c6f1690dc3fb1a565c24f675:reported"
HARNESS2_N=87
LOGS="logs/desktest-train-check-e183.txt:^DESKTEST-TRAIN-CHECK-E183.PASS logs/selftest-rest-e183.txt:^SELFTEST-REST-E183.PASS
logs/dry-intel-e183-v2.txt:^DRY-INTEL-E183-V2.PASS logs/selftest-rb-e183-v3.txt:^SELFTEST-RB-E183-V3.PASS"
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
# 2. step 2 v4, unchanged
bash "$D/s03_desk_e183_v4.sh"
rc=$?
[ "$rc" -eq 0 ] || { echo "[$STEP] STOP: step 2 v4 exited $rc (its STOP line above names why)"; exit "$rc"; }
if [ -n "${RB_DRY:-}" ]; then
  say "note 4's checks on the same HEAD: E183's lists found by SHA256SUMS anywhere in a file's name under $E, nine known (the six gate lists, note 4's among them at its $NOTE4_N entries, each at its count, own bytes and entries; the brief's count and bytes; notes M1's and M2's reported); harness-e183-v2.json re-made; HARNESS OK $HARNESS2_N; note 4's four desk tests' logs"
  exit 0
fi
cd "$REPO" || die 10 "no repository at $REPO"
h1=$(git rev-parse HEAD 2>/dev/null)
bad=""; rep=""
# 3. the lists: every file under E183's directory with SHA256SUMS anywhere in its name, tracked or not
found=$( { git ls-files -- "$E"; find "$E" -type f; } 2>/dev/null | LC_ALL=C sort -u | awk -F/ '$NF ~ /SHA256SUMS/' )
known_names=$(printf '%s\n' "$KNOWN" | cut -d: -f1)
for f in $found; do
  b=$(basename "$f")
  if [ "$(dirname "$f")" != "$E" ] || ! printf '%s\n' "$known_names" | grep -qx "$b"; then
    rep="$rep; $f: a list this step does not know (reported, never a gate; $(grep -c . "$f" 2>/dev/null) lines)"
  fi
done
while IFS=: read -r name pin psha role; do
  [ -n "$name" ] || continue
  p=$E/$name
  if [ ! -f "$p" ]; then
    [ "$role" = reported ] && { rep="$rep; $name missing (reported)"; continue; }
    bad="$bad $name(missing)"; continue
  fi
  n=$(grep -c . "$p"); own=$(shasum -a 256 "$p" | cut -d' ' -f1); okn=$(shasum -a 256 -c "$p" 2>/dev/null | grep -c ': OK$')
  case "$role" in
    gate) { [ "$n" -eq "$pin" ] && [ "$own" = "$psha" ] && [ "$okn" -eq "$n" ]; } || bad="$bad $name($okn OK of $n; pinned $pin and its own bytes${own:+, own ${own:0:12}})" ;;
    bytes) { [ "$n" -eq "$pin" ] && [ "$own" = "$psha" ]; } || bad="$bad $name($n lines; pinned $pin and its own bytes, own ${own:0:12})" ;;
    *) rep="$rep; $name $okn OK of $n (pinned $pin), own bytes $([ "$own" = "$psha" ] && echo 'as pinned' || echo 'NOT as pinned') (reported)" ;;
  esac
done <<EOF2
$KNOWN
EOF2
# 4. the harness v2 and note 4's desk tests' logs
"$PY" -B "$E/make_harness_e183_v2.py" --check > "$RB_OUT/s03v5-harness-remake.txt" 2>&1
grep -q '^CHECK PASS' "$RB_OUT/s03v5-harness-remake.txt" || bad="$bad harness-v2-rebuild"
"$PY" -B "$E/harness_e183_v2.py" > "$RB_OUT/s03v5-harness.txt" 2>&1
grep -q "^HARNESS OK: $HARNESS2_N files" "$RB_OUT/s03v5-harness.txt" || bad="$bad harness-v2($(head -c 200 "$RB_OUT/s03v5-harness.txt"))"
for spec in $LOGS; do
  lf=${spec%%:*}; pat=${spec#*:}
  [ "$(grep -cE "$pat" "$E/$lf" 2>/dev/null)" = 1 ] || bad="$bad $(basename "$lf" .txt)"
done
# 5. the tree did not move
h2=$(git rev-parse HEAD 2>/dev/null)
[ -n "$h1" ] && [ "$h1" = "$h2" ] || die 16 "the lab clone moved during note 4's checks (${h1:0:12} to ${h2:0:12}): run step 2 v5 again"
[ -n "$rep" ] && echo "[$STEP] reported${rep}"
[ -z "$bad" ] || die 16 "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$STEP desk check v5 passed at $h1" >> "$RB_OUT/runbook.log"
say "desk check v5: step 2 v4 passed, then on the same HEAD ${h1:0:12} E183's lists by SHA256SUMS anywhere in a name: the six gate lists at their counts, own bytes and entries (note 4's $NOTE4_N among them), the brief's count and bytes, notes M1's and M2's reported; harness-e183-v2.json re-made; HARNESS OK $HARNESS2_N; note 4's four desk tests' logs as committed"
