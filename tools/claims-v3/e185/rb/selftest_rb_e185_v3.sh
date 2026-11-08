#!/usr/bin/env bash
# E185 (M11's session 3): the desk test of the kit's dated note 2 (KIT.md.dated-note-2.md): step 2 v3 (rb/s03_desk_e185_v3.sh) and the dry
# listing v3 (rb/list_steps_e185_v3.sh). Step 2 reads only the lab clone (git and its files), so it runs here on a SCRATCH CLONE of the
# repository this file sits in: a shared, sparse clone (tools/, workloads/ and the data directories the lists step 2 reads name), with the
# working tree's E185 files committed over its HEAD and a local upstream (a branch of the clone itself), so step 2's pull reads "Already up
# to date" and never reaches the network. Stand-in ssh and rsync first on PATH log any call and refuse it; step 2 makes none. Every case
# that changes a file commits it in the clone (step 2 refuses a dirty tree) and is reset after. The cases:
#   A3  the dry listing v3: every step exits 0, no ssh or rsync call, the look listed before the day's post, step 2 v3 listed twice (step 2,
#       and again just before step 14), step 14 v2 listed after the second;
#   K   step 2 v3 with no window: 10 before any call; with a window written on another day: 10;
#   P0  step 2 v3 on the intact clone: 0, its last line naming the five pins (8, 13, 21, 5 and 28), the kit note 2's count, and note M1
#       "present, its list 21 of 21 at its pinned bytes"; step 2 v2 on the same clone: 0;
#   P1  the kit note 1's list cut to 27 lines: v3 16 ("SHA256SUMS-e185-kit-note1(27 OK of 27; pinned 28"); v2 0 (verify-d2's fault 2, shown);
#   P2  each other list one line short, one at a time (the registration's, the kit's, the runbook's, A1's, the kit note 2's): v3 16 each,
#       the list named with its count and pin;
#   P3  the registration's list with one line repeated (9 lines, every one OK): v3 16 ("9 OK of 9; pinned 8"); v2 0;
#   P4  A1's list with its last line replaced by a copy of its first (5 lines, every one OK, one file no longer pinned: verify-d2's P6
#       class): v3 16 on the list's own bytes; v2 0;
#   P5  a file A1's list pins rewritten together with its line (5 lines, every one OK: verify-d2's P5 class): v3 16 on the list's own bytes;
#       v2 0;
#   M1  note M1's list cut to 20 lines: v3 0, the last line "present, but its list is off its pin (20 OK of 20; pinned 21 ..." and "the M1
#       arm is not read", the same in the runbook's log; note M1 itself removed: v3 0, "absent (not read)";
#   W   step 2 v3 twice in a row on the intact clone, as the kit note 2 runs it (step 2, then again just before step 14): 0 and 0, the
#       paths clean after, nothing appended to the lock file, no call to any box;
#   Z   nothing the test started is left running.
# THE STAND-IN for the kit note 2's list (the real list is written after this test's log, which it pins): in the clone it is replaced by a
# stand-in of exactly the pinned count of real entries (the clone's first rb/*.sh and rb/*.py files, sorted; no case changes them).
#
#   bash tools/claims-v3/e185/rb/selftest_rb_e185_v3.sh <scratch dir outside the repository> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_DRY RB_DESKTEST RB_BASE RB_REPO; do [ -z "${!v:-}" ] || { echo "$v is set: this test sets its own environment"; exit 2; }; done
mkdir -p "$S"
S=$(cd "$S" && pwd -P)
rm -rf "${S:?}/clone" "${S:?}/bin" "${S:?}/out" "${S:?}/dry-out"
C=$S/clone; BIN=$S/bin
mkdir -p "$BIN" "$S/out"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
san() { sed -e "s#$S#<scratch>#g" -e "s#$SRC#<lab clone>#g" | cut -c1-300; }
has() { grep -aqF -- "$1" "$2" && echo 1 || echo 0; }
t_begin=$(date +%s)

# ---- the scratch clone: shared (the objects stay the lab clone's), sparse, the working E185 files committed over HEAD, a local upstream
E=tools/claims-v3/e185
LISTS="m11/SHA256SUMS m11/SHA256SUMS-m11 m11/SHA256SUMS-a1 m11/SHA256SUMS-a2 m11/SHA256SUMS-a3 m11/SHA256SUMS-a4 m11/SHA256SUMS-a5 m11/SHA256SUMS-a6
 m11/SHA256SUMS-a7 m11/SHA256SUMS-a8 m11/SHA256SUMS-a9 m11/SHA256SUMS-a10 m11/SHA256SUMS-score-m11 m11/SHA256SUMS-score-m11-v2 m11/SHA256SUMS-score-m11-v3
 m11/SHA256SUMS-score-m11-v4 m11/SHA256SUMS-score-m11-v5 footing-law/SHA256SUMS footing-law/SHA256SUMS-note1 e185/SHA256SUMS-e185-registration
 e185/SHA256SUMS-e185-kit e185/rb/SHA256SUMS-rb-e185 e185/SHA256SUMS-e185-a1 e185/SHA256SUMS-e185-kit-note1 e185/SHA256SUMS-e185-m1 e185/frozen-e185.sha256"
NEED=$(cd "$SRC/tools/claims-v3" && cat $LISTS | grep -oE 'docs/reports/data/[^/ ]+' | LC_ALL=C sort -u)
G="git -C $C -c user.name=e185-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
git clone -q --shared --no-checkout "$SRC" "$C" || { echo "the scratch clone failed"; exit 2; }
$G sparse-checkout set tools workloads $NEED > /dev/null 2>&1 || { echo "the sparse checkout failed"; exit 2; }
$G checkout -q 2>/dev/null || $G checkout -q "$($G rev-parse --abbrev-ref HEAD)" || { echo "the checkout failed"; exit 2; }
rsync -a --exclude __pycache__ "$SRC/$E/" "$C/$E/"
NPIN=$(sed -n 's/^NOTE2=SHA256SUMS-e185-kit-note2:\([0-9]*\).*/\1/p' "$C/$E/rb/s03_desk_e185_v3.sh")
( cd "$C" && find "$E/rb" -maxdepth 1 -type f \( -name '*.sh' -o -name '*.py' \) | LC_ALL=C sort | head -n "${NPIN:-1}" |
  while IFS= read -r f; do shasum -a 256 "$f"; done ) > "$C/$E/SHA256SUMS-e185-kit-note2"
$G add -A "$E" && $G commit -q -m "E185 runbook v3 desk test: the working E185 files, with the kit note 2's stand-in list" > /dev/null 2>&1
$G branch -q -f frozen HEAD && $G branch -q --set-upstream-to=frozen > /dev/null 2>&1 || { echo "the local upstream failed"; exit 2; }
BASE=$($G rev-parse HEAD)
echo "scratch clone: shared and sparse ($(echo "$NEED" | grep -c .) data directories the lists name), HEAD the lab clone's $($G rev-parse --short HEAD~1) with the working E185 files committed over it; the kit note 2's stand-in list: $(grep -c . "$C/$E/SHA256SUMS-e185-kit-note2") real entries (pin $NPIN)"
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "STAND-IN %s: refused (step 2 reaches no box)" >&2\nexit 97\n' "$n" "$S/calls.log" "$n" > "$BIN/$n"; done
chmod +x "$BIN"/*
export PATH="$BIN:$PATH" RB_REPO="$C" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$RB_LOCK"
R=$C/$E/rb
WDAY=$(date -v+1d +%F)                                          # any day: the window's own file must be written today
win() { RB_OUT="$1" bash "$R/s02_window_e185.sh" "$WDAY" 23:58 23:59 > /dev/null 2>&1; }
reset_clone() { $G reset -q --hard "$BASE"; }
v3() { RB_OUT="$S/out/$1" bash "$R/s03_desk_e185_v3.sh" > "$S/$1.txt" 2>&1; }
v2() { RB_OUT="$S/out/$1" bash "$R/s03_desk_e185_v2.sh" > "$S/$1.txt" 2>&1; }
prep() { mkdir -p "$S/out/$1"; win "$S/out/$1"; }                # a fresh RB_OUT with today's window
commit_change() { $G commit -q -am "$1" > /dev/null 2>&1 || { echo "(the case's commit failed)"; fail=1; }; }
stopline() {  # the step's last word: its STOP line, or its desk-check line with note M1's clause on a line of its own
  grep -m1 -E 'STOP|desk check v[23]:' "$S/$1.txt" | sed 's/; october-forecast-model note M1 .*//' | san
  grep -m1 -oE 'october-forecast-model note M1 .*' "$S/$1.txt" | sed 's/^/    /' | san
}
cd "$C" || exit 2

step "A3. the dry listing v3: every step exits 0, no ssh or rsync call, the look before the post, step 2 v3 twice, step 14 v2 after the second"
: > "$S/calls.log"
bash "$R/list_steps_e185_v3.sh" "$S/dry-out" > "$S/dry-listing-v3.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing-v3.txt"
o=$(awk '/^################ s05_look_e185.sh aifoundry3$/ {l=NR} /^################ step 4: the day.s one post/ {p=NR}
         /^################ s03_desk_e185_v3.sh$/ {k++; d[k]=NR} /^################ s22_collect_e185_v2.sh$/ {c=NR}
         END {print ((l > 0 && p > l) ? "look-first" : "POST-FIRST") "." k "." ((k == 2 && c > d[2] && d[2] > p) ? "14-after" : "ORDER")}' "$S/dry-listing-v3.txt")
echo "calls: $n; $o"
ok "$rc.$n.$o" "0.0.look-first.2.14-after" "A3 the dry listing v3: 0 failing, no call, the look before the post, step 2 v3 listed twice, step 14 v2 after the second"

step "K. step 2 v3 without the go's window, then with a window written on another day: refused before any call"
mkdir -p "$S/out/K1"; : > "$S/calls.log"
v3 K1; k1=$?; stopline K1
prep K2; touch -t "$(date -v-1d +%Y%m%d%H%M)" "$S/out/K2/window.env"
v3 K2; k2=$?; stopline K2
n=$(grep -c . "$S/calls.log")
ok "$k1.$k2.$n" "10.10.0" "K no window 10; a window from another day 10; no call either time"

step "P0. step 2 v3 on the intact clone (the five lists at their pins and bytes, the kit note 2's stand-in at its count, note M1 present)"
prep P0; v3 P0; p0=$?; stopline P0
pins=$(has "E185's five lists at their pinned counts and bytes (8, 13, 21, 5 and 28) and the kit note 2's at its count ($NPIN)" "$S/P0.txt")
m1=$(has "october-forecast-model note M1 present, its list 21 of 21 at its pinned bytes" "$S/P0.txt")
prep P0v2; v2 P0v2; p0b=$?; stopline P0v2
ok "$p0.$pins.$m1.$p0b" "0.1.1.0" "P0 v3 passes the intact tree, naming the pins and note M1 present at 21 of 21; v2 passes it too"

step "P1. the kit note 1's list cut to 27 lines and committed (verify-d2's case): v3 refuses, v2 passes"
sed -i '' '$d' "$C/$E/SHA256SUMS-e185-kit-note1"; commit_change "P1: the kit note 1's list one line short"
prep P1; v3 P1; r3=$?; stopline P1
q=$(has "SHA256SUMS-e185-kit-note1(27 OK of 27; pinned 28" "$S/P1.txt")
prep P1v2; v2 P1v2; r2=$?; stopline P1v2
reset_clone
ok "$r3.$q.$r2" "16.1.0" "P1 the kit note 1's list at 27: v3 16 naming its count and pin; v2 0 (the fault, shown)"

step "P2. each other list one line short, one at a time: v3 refuses each, naming it"
got=""
for spec in SHA256SUMS-e185-registration:8 SHA256SUMS-e185-kit:13 rb/SHA256SUMS-rb-e185:21 SHA256SUMS-e185-a1:5 SHA256SUMS-e185-kit-note2:$NPIN; do
  l=${spec%%:*}; pin=${spec##*:}; b=$(basename "$l")
  sed -i '' '$d' "$C/$E/$l"; commit_change "P2: $b one line short"
  prep "P2-$b"; v3 "P2-$b"; r=$?
  q=$(has "$b($((pin - 1)) OK of $((pin - 1)); pinned $pin" "$S/P2-$b.txt")
  echo "  $b: rc $r, named $q"
  got="$got $r.$q"
  reset_clone
done
ok "$(echo $got)" "16.1 16.1 16.1 16.1 16.1" "P2 the registration's, the kit's, the runbook's, A1's and the kit note 2's lists one line short: 16 each, named"

step "P3. the registration's list with one line repeated (9 lines, every one OK): v3 refuses, v2 passes"
head -n 1 "$C/$E/SHA256SUMS-e185-registration" >> "$C/$E/SHA256SUMS-e185-registration"; commit_change "P3: a line repeated"
prep P3; v3 P3; r3=$?; stopline P3
q=$(has "SHA256SUMS-e185-registration(9 OK of 9; pinned 8" "$S/P3.txt")
prep P3v2; v2 P3v2; r2=$?
reset_clone
ok "$r3.$q.$r2" "16.1.0" "P3 a repeated line: v3 16 (9 of 9 against the pin 8); v2 0"

step "P4. A1's list with its last line replaced by a copy of its first (5 lines, every one OK; one file no longer pinned): v3 refuses on the bytes, v2 passes"
f=$C/$E/SHA256SUMS-e185-a1; { sed '$d' "$f"; head -n 1 "$f"; } > "$S/a1-p4"; cp "$S/a1-p4" "$f"; commit_change "P4: a line replaced by a copy of another"
prep P4; v3 P4; r3=$?; stopline P4
q=$(has "SHA256SUMS-e185-a1(5 OK of 5; pinned 5; its own bytes differ from the pin)" "$S/P4.txt")
prep P4v2; v2 P4v2; r2=$?
reset_clone
ok "$r3.$q.$r2" "16.1.0" "P4 a copied line (the count kept): v3 16 on the list's own bytes; v2 0"

step "P5. a file A1's list pins (a1-e185.txt) rewritten together with its line: v3 refuses on the bytes, v2 passes"
echo "(desk test P5: one line appended)" >> "$C/$E/a1-e185.txt"
h=$(cd "$C" && shasum -a 256 "$E/a1-e185.txt")
f=$C/$E/SHA256SUMS-e185-a1; awk -v h="$h" -v p="$E/a1-e185.txt" '$2 == p {print h; next} {print}' "$f" > "$S/a1-p5"; cp "$S/a1-p5" "$f"
commit_change "P5: a file and its line rewritten together"
prep P5; v3 P5; r3=$?; stopline P5
q=$(has "SHA256SUMS-e185-a1(5 OK of 5; pinned 5; its own bytes differ from the pin)" "$S/P5.txt")
prep P5v2; v2 P5v2; r2=$?
reset_clone
ok "$r3.$q.$r2" "16.1.0" "P5 a file rewritten with its line (the count kept, every line OK): v3 16 on the list's own bytes; v2 0"

step "M1. note M1's list cut to 20 lines: reported, never a gate; then note M1 removed"
sed -i '' '$d' "$C/$E/SHA256SUMS-e185-m1"; commit_change "M1: note M1's list one line short"
prep M1a; v3 M1a; ra=$?; stopline M1a
qa=$(has "october-forecast-model note M1 present, but its list is off its pin (20 OK of 20; pinned 21" "$S/M1a.txt")
qa2=$(has "the M1 arm is not read on this day" "$S/M1a.txt")
la=$(grep -c "step=s03_desk_v3_e185 october-forecast-model note M1 present, but its list is off its pin" "$S/out/M1a/runbook.log")
reset_clone
$G rm -q "$E/E185.md.dated-note-M1.md"; commit_change "M1: note M1 removed"
prep M1b; v3 M1b; rb=$?; stopline M1b
qb=$(has "october-forecast-model note M1 absent (not read)" "$S/M1b.txt")
reset_clone
ok "$ra.$qa.$qa2.$la.$rb.$qb" "0.1.1.1.0.1" "M1 a short M1 list: 0, the miss named and logged, the arm not read; M1 removed: 0, absent"

step "W. step 2 v3 twice in a row, as the kit note 2 runs it (step 2, then again just before step 14)"
: > "$S/calls.log"; l0=$(grep -c . "$RB_LOCK")
prep W; RB_OUT="$S/out/W" bash "$R/s03_desk_e185_v3.sh" > "$S/W1.txt" 2>&1; w1=$?
RB_OUT="$S/out/W" bash "$R/s03_desk_e185_v3.sh" > "$S/W2.txt" 2>&1; w2=$?
stopline W2
st=$($G status --short "$E" tools/claims-v3/m11 tools/claims-v3/footing-law | grep -c .)
l1=$(grep -c . "$RB_LOCK"); n=$(grep -c . "$S/calls.log")
k=$(grep -c 'step=s03_desk_v3_e185 october-forecast-model note M1 present, its list 21 of 21' "$S/out/W/runbook.log")
ok "$w1.$w2.$st.$l0.$l1.$n.$k" "0.0.0.0.0.0.2" "W twice: 0 and 0, the paths clean, the lock file unchanged, no call, note M1's line logged twice"

step "Z. nothing the test started is left running"
left=$(pgrep -f "$S/clone" 2>/dev/null | grep -c .)
echo "processes under the scratch clone: $left"
ok "$left" 0 "Z nothing left running"

echo
echo "calls to any box by the stand-ins: $(grep -c . "$S/calls.log"); elapsed $(( $(date +%s) - t_begin )) s"
echo "SELFTEST-RB-E185-V3 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL), $npass of $ncase"
exit "$fail"
