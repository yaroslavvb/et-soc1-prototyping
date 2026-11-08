#!/usr/bin/env bash
# E185 and E183, day 2: the desk test of the day-2 check (rb/check_day2_v1.py), E185's step 2 v4 (rb/s03_desk_e185_v4.sh), E183's step 2 v3
# (../../e183/rb/s03_desk_e183_v3.sh) and their dry listings (E185's kit dated note 3, E183's kit dated note 2). The steps read only the lab
# clone (git and its files), so they run here on a SCRATCH CLONE: a shared, sparse clone (tools/, workloads/ and the data directories the
# day's lists name) of a local bare upstream, itself a shared clone of the repository this file sits in, with the working E183 and E185
# files committed over its HEAD and pushed to the upstream; a helper clone of the upstream makes "the lab moved" cases. Stand-in ssh,
# rsync and scp first on PATH log any call and refuse it; no step here makes one. Every case that changes a file commits it in the clone
# (or leaves it uncommitted where the case says so) and is reset after. The cases (verify-d2b's H numbers where it made them):
#   A   the dry listings: E185's v4 and E183's v3 exit 0 with no call; E185's lists step 2 v4 twice, the look before the post, step 14
#       after the second step 2, and the M1 gate after step 14; E183's lists step 2 v3, the look before the post, and its M1 gate;
#   K   no window, then a window written on another day: E185 v4 10 and E183 v3 10 each time, before the day-2 check (no call, no pull);
#   P0  the intact clone: the day-2 check 0; E185 v4 0, E183 v3 0; and step 2 v3, v2 and E183's v2 each 0 (the new files break none);
#   H2b E185's brief rewritten together with its line in the kit note 2's list: v4 16; v3 alone 0 (the fault, re-made);
#   H2c E185's M1 reader rewritten together with its line in the M1 list: v4 0, the M1 change reported, never a gate; the M1 gate 16, the
#       reader not run;
#   H2d M11's scorer v5 rewritten together with its line in SHA256SUMS-score-m11-v5: v4 16; v3 alone 0 (the fault, re-made);
#   H2f E183's M1 reader rewritten together with its line in the M1 list: E183 v3 0, the change and E183's brief list's two M1 entries
#       reported; the M1 gate for E183 16, the reader not run;
#   H3b the kit note 2's line for E185's brief replaced by a copy of another line, the brief changed: v4 16;
#   H3c SHA256SUMS-score-m11-v5's line for the scorer replaced by a copy of another, the scorer changed: v4 16;
#   H4e SHA256SUMS-score-m11-v5 reordered (every line OK): v4 16;
#   H7  E183's brief changed and committed: E183 v3 16 and E185 v4 16; E183's v2 alone 0 (the fault, re-made);
#   AD1  a dated note M2 added under e185: v4 0, the addition counted (one more than P0's);
#   AD2  a json.py added beside E185's readers: v4 16 and E183 v3 16 (it shadows the standard module);
#   AD3  a byte-code file forced in under m11/__pycache__: v4 16;
#   AD4  an e185/score_m11_v4.py added (M11's scorer v5 puts E185's directory first on sys.path): v4 16, its module name another's;
#   AD5  an e185/numpy.py added (M11's scorers import numpy from the user site): v4 16, it shadows the module;
#   S1  E183's brief changed and NOT committed: E185 v4 16 (status on the day's paths); v3 alone 0 (its status reads E185's paths only);
#   R1  the M1 gate for E185 after a committed stand-in data directory (a score reading NOT SCORED), with step 2's M1 line in E185's
#       RB_OUT: 0, the reader run (rc 0, "not read"), its two outputs the only new files;
#   R2  the same with the data directory not committed: 16, the reader not run;
#   R3  the same with an RB_OUT whose log holds no step 2 M1 line: 16;
#   R4  the M1 gate for E183 after a committed stand-in data directory with no reduction: 0, the reader run and its rc 1 printed (a
#       reader's failure never blocks), nothing written;
#   R5  a data directory that is not the run's: 10;
#   L1  step 2 v4 0; then the upstream gains a commit rewriting the launch step with its line in the kit note 1's list (the lab moved);
#       step 2 v4 again, as before step 14: it pulls, then 16;
#   LM  the upstream gains an addition between the day-2 check's pull and step 2 v3's (a hook in the clone): v4 16, "moved during step 2";
#   D   a diverged clone: v4 16, the pull "not the network's";
#   X   a detached HEAD: v4 16, the pull "not the network's";
#   U   the upstream gone: v4 16, the pull "the network's";
#   C   coverage: every file the day's 32 lists, E183's harness and E185's runbook pins name lies under the day-2 check's paths;
#   Z   nothing the test started is left running.
#
#   bash tools/claims-v3/e185/rb/selftest_day2_v1.sh <scratch dir outside the repository> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_DRY RB_DESKTEST RB_BASE RB_REPO; do [ -z "${!v:-}" ] || { echo "$v is set: this test sets its own environment"; exit 2; }; done
mkdir -p "$S"
S=$(cd "$S" && pwd -P)
rm -rf "${S:?}/clone" "${S:?}/up.git" "${S:?}/up.gone" "${S:?}/helper" "${S:?}/bin" "${S:?}/out" "${S:?}/dry5" "${S:?}/dry3"
C=$S/clone; UP=$S/up.git; H=$S/helper; BIN=$S/bin
PY=/usr/bin/python3
mkdir -p "$BIN" "$S/out"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
san() { sed -e "s#$S#<scratch>#g" -e "s#$SRC#<lab clone>#g" | cut -c1-330; }
has() { grep -aqF -- "$1" "$2" && echo 1 || echo 0; }
t_begin=$(date +%s)
WDAY=$(date -v+1d +%F)                                          # any day: the window's own file must be written today
D5=docs/reports/data/$WDAY-e185-m11-session3-aifoundry3; D3=docs/reports/data/$WDAY-e183-vector-add-r2-aifoundry3

# ---- the upstream, the clone and the helper: shared objects, sparse trees, the working E183 and E185 files committed and pushed
NEED=$(cd "$SRC/tools/claims-v3" && cat m11/SHA256SUMS m11/SHA256SUMS-m11 m11/SHA256SUMS-a* m11/SHA256SUMS-score-m11* footing-law/SHA256SUMS* \
  e185/SHA256SUMS-e185-registration e185/SHA256SUMS-e185-kit e185/rb/SHA256SUMS-rb-e185 e185/SHA256SUMS-e185-a1 e185/SHA256SUMS-e185-kit-note1 \
  e185/SHA256SUMS-e185-kit-note2 e185/SHA256SUMS-e185-m1 e185/frozen-e185.sha256 e183/SHA256SUMS-e183-registration e183/SHA256SUMS-e183-kit \
  e183/SHA256SUMS-e183-note1 e183/SHA256SUMS-e183-brief e183/SHA256SUMS-e183-m1 | grep -oE 'docs/reports/data/[^/ ]+' | LC_ALL=C sort -u)
git clone -q --bare --shared "$SRC" "$UP" || { echo "the upstream failed"; exit 2; }
gx() { local d=$1; shift; git -C "$d" -c user.name=day2-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false "$@"; }
for k in "$C" "$H"; do
  git clone -q --shared --no-checkout "$UP" "$k" || { echo "a clone failed"; exit 2; }
  gx "$k" sparse-checkout set tools workloads $NEED "$D5" "$D3" > /dev/null 2>&1 || { echo "the sparse checkout failed"; exit 2; }
  gx "$k" checkout -q || { echo "the checkout failed"; exit 2; }
done
rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/e185/" "$C/tools/claims-v3/e185/"
rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/e183/" "$C/tools/claims-v3/e183/"
gx "$C" add -A tools/claims-v3/e185 tools/claims-v3/e183 && gx "$C" commit -q -m "day-2 desk test: the working E183 and E185 files" > /dev/null 2>&1
gx "$C" push -q origin HEAD:main > /dev/null 2>&1 || { echo "the push to the upstream failed"; exit 2; }
gx "$H" pull -q --ff-only > /dev/null 2>&1 || { echo "the helper's pull failed"; exit 2; }
BASE=$(gx "$C" rev-parse HEAD)
echo "scratch clone: shared and sparse ($(echo "$NEED" | grep -c .) data directories the lists name), HEAD the lab clone's $(gx "$C" rev-parse --short HEAD~1) with the working E183 and E185 files committed over it ($(gx "$C" show --stat --format= HEAD | tail -n 1 | sed 's/^ *//')); a local bare upstream and a helper clone of it"
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "STAND-IN %s: refused (step 2 reaches no box)" >&2\nexit 97\n' "$n" "$S/calls.log" "$n" > "$BIN/$n"; done
chmod +x "$BIN"/*
export PATH="$BIN:$PATH" RB_REPO="$C" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$RB_LOCK"
R5=$C/tools/claims-v3/e185/rb; R3=$C/tools/claims-v3/e183/rb; E5=tools/claims-v3/e185; E3=tools/claims-v3/e183; M11=tools/claims-v3/m11
prep5() { mkdir -p "$S/out/$1"; RB_OUT="$S/out/$1" bash "$R5/s02_window_e185.sh" "$WDAY" 23:58 23:59 > /dev/null 2>&1; }
prep3() { mkdir -p "$S/out/$1"; RB_OUT="$S/out/$1" bash "$R3/s02_window_e183.sh" "$WDAY" 23:58 23:59 > /dev/null 2>&1; }
v4() { RB_OUT="$S/out/$1" bash "$R5/s03_desk_e185_v4.sh" > "$S/$1.txt" 2>&1; }
v3() { RB_OUT="$S/out/$1" bash "$R5/s03_desk_e185_v3.sh" > "$S/$1.txt" 2>&1; }
v2() { RB_OUT="$S/out/$1" bash "$R5/s03_desk_e185_v2.sh" > "$S/$1.txt" 2>&1; }
e3() { RB_OUT="$S/out/$1" bash "$R3/s03_desk_e183_v3.sh" > "$S/$1.txt" 2>&1; }
e2() { RB_OUT="$S/out/$1" bash "$R3/s03_desk_e183_v2.sh" > "$S/$1.txt" 2>&1; }
chk() { "$PY" -I -B "$R5/check_day2_v1.py" "$@"; }
reset_clone() { gx "$C" checkout -q main 2>/dev/null; gx "$C" reset -q --hard "$BASE"; gx "$C" clean -q -fdx -- tools workloads docs > /dev/null 2>&1; }
reset_up() { git -C "$UP" update-ref refs/heads/main "$BASE"; gx "$H" fetch -q origin; gx "$H" reset -q --hard "$BASE"; gx "$C" fetch -q origin; }
commit_all() {  # every change under tools/ and workloads/, and the stand-in data directories where a case made them
  local d extra=()
  for d in "$D5" "$D3"; do [ -d "$C/$d" ] && extra+=("$d"); done
  gx "$C" add -A tools workloads ${extra[@]+"${extra[@]}"} && gx "$C" commit -q -m "$1" > /dev/null 2>&1 || { echo "(the case's commit failed)"; fail=1; }
}
relist() {  # relist <list> <file>: the file's line in the list rewritten to its new hash (a file rewritten together with its line)
  local h; h=$(cd "$C" && shasum -a 256 "$2")
  awk -v h="$h" -v p="$2" '$2 == p {print h; next} {print}' "$C/$1" > "$S/relist.tmp" && cp "$S/relist.tmp" "$C/$1"
}
stopline() {  # the step's own last word: its first STOP line, else its last desk-check line (the outer step's, for v4 and E183's v3)
  if grep -q 'STOP' "$S/$1.txt"; then grep -m1 'STOP' "$S/$1.txt" | san
  else grep -E 'desk check v[0-9]:' "$S/$1.txt" | tail -n 1 | sed 's/; october-forecast-model note M1 .*//' | san; fi
}
cd "$C" || exit 2

step "A. the dry listings: E185's v4 and E183's v3, every step exiting 0 with no call, in their order"
: > "$S/calls.log"
bash "$R5/list_steps_e185_v4.sh" "$S/dry5" > "$S/dry-listing-v4.txt" 2>&1; ra=$?
bash "$R3/list_steps_e183_v3.sh" "$S/dry3" > "$S/dry-listing-e183-v3.txt" 2>&1; rb=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing-v4.txt"; tail -n 1 "$S/dry-listing-e183-v3.txt"
o5=$(awk '/^################ s05_look_e185.sh aifoundry3$/ {l=NR} /^################ step 4: the day.s one post/ {p=NR}
          /^################ s03_desk_e185_v4.sh$/ {k++; d[k]=NR} /^################ s22_collect_e185_v2.sh$/ {c=NR} /check_day2_v1.py m1 e185/ {m=NR}
          END {print ((l > 0 && p > l) ? "look-first" : "POST-FIRST") "." k "." ((k == 2 && c > d[2] && d[2] > p) ? "14-after" : "ORDER") "." ((m > c) ? "m1-after" : "M1")}' "$S/dry-listing-v4.txt")
o3=$(awk '/s03_desk_e183_v3.sh/ && /^################/ {k++} /k6\/s05_look_k6.sh aifoundry3$/ {l=NR} /the day.s one post, made AFTER/ {p=NR}
          /s22_collect_e183_v2.sh/ && /^################/ {c=NR} /check_day2_v1.py m1 e183/ {m=NR}
          END {print k "." ((l > 0 && p > l) ? "look-first" : "POST-FIRST") "." ((m > c) ? "m1-after" : "M1")}' "$S/dry-listing-e183-v3.txt")
echo "calls: $n; E185 $o5; E183 $o3"
ok "$ra.$rb.$n.$o5.$o3" "0.0.0.look-first.2.14-after.m1-after.1.look-first.m1-after" "A the dry listings: 0 failing, no call, the look before the post, E185's step 2 v4 twice with step 14 after the second, each M1 gate after its collection"

step "K. no window, then a window written on another day: refused before the day-2 check"
: > "$S/calls.log"
mkdir -p "$S/out/K1" "$S/out/K3"; v4 K1; k1=$?; stopline K1; e3 K3; k3=$?; stopline K3
prep5 K2; touch -t "$(date -v-1d +%Y%m%d%H%M)" "$S/out/K2/window.env"; v4 K2; k2=$?; stopline K2
prep3 K4; touch -t "$(date -v-1d +%Y%m%d%H%M)" "$S/out/K4/window.env"; e3 K4; k4=$?; stopline K4
nchk=$(cat "$S/out/K1/runbook.log" "$S/out/K2/runbook.log" "$S/out/K3/runbook.log" "$S/out/K4/runbook.log" 2>/dev/null | grep -c 'day-2 check')
n=$(grep -c . "$S/calls.log")
ok "$k1-$k2-$k3-$k4-$nchk-$n" "10-10-10-10-0-0" "K E185 v4 and E183 v3: 10 without a window and 10 with another day's, the day-2 check never reached, no call"

step "P0. the intact clone: the day-2 check, E185 v4, E183 v3, and the earlier step 2s"
chk tree > "$S/P0c.txt" 2>&1; pc=$?; grep -E 'DAY2-CHECK|the day.s paths' "$S/P0c.txt" | san
prep5 P0; v4 P0; p4=$?; stopline P0
prep3 P0e3; e3 P0e3; pe3=$?; stopline P0e3
prep5 P0v3; v3 P0v3; p3=$?; prep5 P0v2; v2 P0v2; p2=$?; prep3 P0e2; e2 P0e2; pe2=$?
base_adds=$(sed -nE 's/.* ([0-9]+) file\(s\) added since 6860643c.*/\1/p' "$S/P0c.txt" | head -n 1); echo "  additions since 6860643c in the day's directories at the clone's HEAD (this kit's new files): $base_adds"
q=$(has "DAY2-CHECK OK at $(gx "$C" rev-parse --short=12 HEAD)" "$S/P0.txt"); q2=$(has "october-forecast-model note M1 present, its list 21 of 21 at its pinned bytes" "$S/P0.txt")
echo "  E185 v3 alone $p3, E185 v2 $p2, E183 v2 $pe2"
ok "$pc.$p4.$q.$q2.$pe3.$p3.$p2.$pe2" "0.0.1.1.0.0.0.0" "P0 the check 0; E185 v4 0 (the check OK at HEAD, then v3's M1 line 21 of 21); E183 v3 0; v3, v2 and E183's v2 each 0"

step "H2b. E185's brief rewritten together with its line in the kit note 2's list: v4 refuses, v3 alone passes"
echo "(desk test H2b: one line appended)" >> "$C/$E5/CARD-LANE-BRIEF.md"; relist "$E5/SHA256SUMS-e185-kit-note2" "$E5/CARD-LANE-BRIEF.md"; commit_all "H2b"
prep5 H2b; v4 H2b; r4=$?; stopline H2b
q=$(has "e185/SHA256SUMS-e185-kit-note2 (its own bytes differ from the pin)" "$S/H2b.txt"); q2=$(has "M $E5/CARD-LANE-BRIEF.md" "$S/H2b.txt")
prep5 H2bv3; v3 H2bv3; r3=$?
reset_clone
ok "$r4.$q.$q2.$r3" "16.1.1.0" "H2b v4 16 (the kit note 2's list off its bytes; the brief's change in the history); v3 0 (the fault, re-made)"

step "H2c. E185's M1 reader rewritten together with its line in the M1 list: v4 passes (reported), the M1 gate refuses"
echo "# desk test H2c" >> "$C/$E5/arm_m1_read_e185.py"; relist "$E5/SHA256SUMS-e185-m1" "$E5/arm_m1_read_e185.py"
mkdir -p "$C/$D5"; echo "stand-in data README (desk test)" > "$C/$D5/README.md"; commit_all "H2c"
prep5 H2c; v4 H2c; r4=$?; stopline H2c
q=$(has "M1 files changed since 6860643c (reported" "$S/H2c.txt"); q2=$(has "but its list is off its pin" "$S/H2c.txt")
chk m1 e185 --data "$D5" --rb-out "$S/out/H2c" > "$S/H2cg.txt" 2>&1; rg=$?; grep -m1 'STOP' "$S/H2cg.txt" | san
q3=$(has "READER-RC" "$S/H2cg.txt"); q4=$(has "e185/SHA256SUMS-e185-m1: 21 OK of 21; pinned 21; its own bytes differ from the pin" "$S/H2cg.txt")
reset_clone
ok "$r4.$q.$q2.$rg.$q3.$q4" "0.1.1.16.0.1" "H2c v4 0 with the M1 change reported; the M1 gate 16 on the list's own bytes, the reader not run"

step "H2d. M11's scorer v5 rewritten together with its line in SHA256SUMS-score-m11-v5: v4 refuses, v3 alone passes"
echo "# desk test H2d" >> "$C/$M11/score_m11_v5.py"; relist "$M11/SHA256SUMS-score-m11-v5" "$M11/score_m11_v5.py"; commit_all "H2d"
prep5 H2d; v4 H2d; r4=$?; stopline H2d
q=$(has "m11/SHA256SUMS-score-m11-v5 (its own bytes differ from the pin)" "$S/H2d.txt"); q2=$(has "M $M11/score_m11_v5.py" "$S/H2d.txt")
prep5 H2dv3; v3 H2dv3; r3=$?
reset_clone
ok "$r4.$q.$q2.$r3" "16.1.1.0" "H2d v4 16 (the scorer's list off its bytes; the scorer's change in the history); v3 0 (the fault, re-made)"

step "H2f. E183's M1 reader rewritten together with its line: E183 v3 passes (reported), the M1 gate for E183 refuses"
echo "# desk test H2f" >> "$C/$E3/arm_m1_read_e183.py"; relist "$E3/SHA256SUMS-e183-m1" "$E3/arm_m1_read_e183.py"
mkdir -p "$C/$D3"; echo "stand-in data README (desk test)" > "$C/$D3/README.md"; commit_all "H2f"
prep3 H2f; e3 H2f; r3=$?; stopline H2f
q=$(has "M1 files changed since 6860643c (reported" "$S/H2f.txt"); q2=$(has "its 5 M1 entries 2 not OK (reported, never a gate)" "$S/H2f.txt")
chk m1 e183 --data "$D3" > "$S/H2fg.txt" 2>&1; rg=$?; grep -m1 'STOP' "$S/H2fg.txt" | san
q3=$(has "READER-RC" "$S/H2fg.txt")
reset_clone
ok "$r3.$q.$q2.$rg.$q3" "0.1.1.16.0" "H2f E183 v3 0, the M1 change and the brief list's two M1 entries reported; the M1 gate 16, the reader not run"

step "H3b. the kit note 2's line for E185's brief replaced by a copy of another line, the brief changed: v4 refuses"
f=$C/$E5/SHA256SUMS-e185-kit-note2; awk -v p="$E5/CARD-LANE-BRIEF.md" -v c="$(sed -n 3p "$f")" '$2 == p {print c; next} {print}' "$f" > "$S/h3b"; cp "$S/h3b" "$f"
echo "(desk test H3b)" >> "$C/$E5/CARD-LANE-BRIEF.md"; commit_all "H3b"
prep5 H3b; v4 H3b; r4=$?; stopline H3b
reset_clone
ok "$r4" "16" "H3b a copied line (the count kept, every line OK): v4 16"

step "H3c. SHA256SUMS-score-m11-v5's line for the scorer replaced by a copy of another, the scorer changed: v4 refuses"
f=$C/$M11/SHA256SUMS-score-m11-v5; awk -v p="$M11/score_m11_v5.py" -v c="$(sed -n 2p "$f")" '$2 == p {print c; next} {print}' "$f" > "$S/h3c"; cp "$S/h3c" "$f"
echo "# desk test H3c" >> "$C/$M11/score_m11_v5.py"; commit_all "H3c"
prep5 H3c; v4 H3c; r4=$?; stopline H3c
reset_clone
ok "$r4" "16" "H3c a copied line in M11's list (the count kept, every line OK): v4 16"

step "H4e. SHA256SUMS-score-m11-v5 reordered (every line OK): v4 refuses"
f=$C/$M11/SHA256SUMS-score-m11-v5; { tail -n 1 "$f"; sed '$d' "$f"; } > "$S/h4e"; cp "$S/h4e" "$f"; commit_all "H4e"
prep5 H4e; v4 H4e; r4=$?; stopline H4e
reset_clone
ok "$r4" "16" "H4e M11's list reordered: v4 16"

step "H7. E183's brief changed and committed: E183 v3 and E185 v4 refuse; E183's v2 alone passes"
echo "(desk test H7)" >> "$C/$E3/CARD-LANE-BRIEF.md"; commit_all "H7"
prep3 H7; e3 H7; r3=$?; stopline H7
prep5 H7v4; v4 H7v4; r4=$?; prep3 H7e2; e2 H7e2; r2=$?
q=$(has "e183/SHA256SUMS-e183-brief (1 entry not OK: $E3/CARD-LANE-BRIEF.md)" "$S/H7.txt")
reset_clone
ok "$r3.$r4.$q.$r2" "16.16.1.0" "H7 E183 v3 16 and E185 v4 16, the brief named; E183's v2 0 (the fault, re-made)"

step "AD1. a dated note M2 added under e185: v4 passes, the addition counted"
echo "stand-in M2 note (desk test)" > "$C/$E5/E185.md.dated-note-M2.md"; commit_all "AD1"
prep5 AD1; v4 AD1; r4=$?; stopline AD1
q=$(has "$((base_adds + 1)) file(s) added since 6860643c in the day's" "$S/AD1.txt")
reset_clone
ok "$r4.$q" "0.1" "AD1 an added dated note: v4 0, counted"

step "AD2. a json.py added beside E185's readers: v4 and E183 v3 refuse (it shadows the standard module)"
echo "# desk test AD2" > "$C/$E5/json.py"; commit_all "AD2"
prep5 AD2; v4 AD2; r4=$?; stopline AD2
prep3 N2e3; e3 N2e3; r3=$?
q=$(has "$E5/json.py (shadows the module 'json'" "$S/AD2.txt")
reset_clone
ok "$r4.$r3.$q" "16.16.1" "AD2 an added json.py: v4 16 and E183 v3 16, named as shadowing"

step "AD3. a byte-code file forced in under m11/__pycache__: v4 refuses"
mkdir -p "$C/$M11/__pycache__"; printf 'desk test AD3' > "$C/$M11/__pycache__/score_m11_v4.cpython-39.pyc"
gx "$C" add -f "$M11/__pycache__/score_m11_v4.cpython-39.pyc" && gx "$C" commit -q -m "AD3" > /dev/null 2>&1
prep5 AD3; v4 AD3; r4=$?; stopline AD3
q=$(has "a byte-code or .pth file" "$S/AD3.txt")
reset_clone
ok "$r4.$q" "16.1" "AD3 an added byte-code file: v4 16"

step "AD4. an e185/score_m11_v4.py added (a module name of M11's): v4 refuses"
echo "# desk test AD4" > "$C/$E5/score_m11_v4.py"; commit_all "AD4"
prep5 AD4; v4 AD4; r4=$?; stopline AD4
q=$(has "$E5/score_m11_v4.py (its module name 'score_m11_v4' is also $M11/score_m11_v4.py's)" "$S/AD4.txt")
reset_clone
ok "$r4.$q" "16.1" "AD4 an added file sharing a module name with M11's v4: v4 16, named"

step "AD5. an e185/numpy.py added (the scorers' numpy is in the user site): v4 refuses"
echo "# desk test AD5" > "$C/$E5/numpy.py"; commit_all "AD5"
prep5 AD5; v4 AD5; r4=$?; stopline AD5
q=$(has "$E5/numpy.py (shadows the module 'numpy' the system python finds)" "$S/AD5.txt")
reset_clone
ok "$r4.$q" "16.1" "AD5 an added numpy.py: v4 16, named as shadowing"

step "S1. E183's brief changed and not committed: E185 v4 refuses (status); v3 alone passes"
echo "(desk test S1)" >> "$C/$E3/CARD-LANE-BRIEF.md"
prep5 S1; v4 S1; r4=$?; stopline S1
q=$(has "status: 1 uncommitted change(s) on the day's paths: M $E3/CARD-LANE-BRIEF.md" "$S/S1.txt")
prep5 S1v3; v3 S1v3; r3=$?
reset_clone
ok "$r4.$q.$r3" "16.1.0" "S1 an uncommitted E183 brief: E185 v4 16 (status, named); v3 0"

step "R. the M1 readers' gate on the intact tree"
mkdir -p "$C/$D5" "$C/$D3"; echo "stand-in data README (desk test)" > "$C/$D5/README.md"; echo "stand-in data README (desk test)" > "$C/$D3/README.md"
echo '{"E185": {"reads": "NOT SCORED (desk test stand-in)"}}' > "$C/$D5/scored-m11.json"
commit_all "R: stand-in data directories"
prep5 R1; v4 R1 > /dev/null 2>&1
chk m1 e185 --data "$D5" --rb-out "$S/out/R1" > "$S/R1.txt" 2>&1; r1=$?; grep -E 'M1-READER|READER-RC|M1 reader outputs' "$S/R1.txt" | san
q1=$(has "M1-READER-GATE e185 OK" "$S/R1.txt"); q1b=$(has "READER-RC 0" "$S/R1.txt"); cnt1=$(gx "$C" status --porcelain --untracked-files=all | grep -c .)
gx "$C" clean -q -fdx -- docs > /dev/null 2>&1
echo x > "$C/$D5/extra-uncommitted.txt"
chk m1 e185 --data "$D5" --rb-out "$S/out/R1" > "$S/R2.txt" 2>&1; r2=$?; grep -m1 STOP "$S/R2.txt" | san
q2=$(has "READER-RC" "$S/R2.txt")
gx "$C" clean -q -fdx -- docs > /dev/null 2>&1
mkdir -p "$S/out/R3"; chk m1 e185 --data "$D5" --rb-out "$S/out/R3" > "$S/R3.txt" 2>&1; r3=$?; grep -m1 STOP "$S/R3.txt" | san
chk m1 e183 --data "$D3" > "$S/R4.txt" 2>&1; r4=$?; grep -E 'M1-READER|READER-RC|M1 reader outputs' "$S/R4.txt" | san
q4=$(has "M1-READER-GATE e183 OK" "$S/R4.txt"); q4b=$(has "READER-RC 1" "$S/R4.txt"); cnt4=$(gx "$C" status --porcelain --untracked-files=all | grep -c .)
gx "$C" clean -q -fdx -- docs > /dev/null 2>&1
chk m1 e185 --data "$E5" --rb-out "$S/out/R1" > "$S/R5.txt" 2>&1; r5=$?; grep -m1 STOP "$S/R5.txt" | san
reset_clone
ok "$r1.$q1.$q1b.$cnt1.$r2.$q2.$r3.$r4.$q4.$q4b.$cnt4.$r5" "0.1.1.2.16.0.16.0.1.1.0.10" "R1 E185's gate 0, the reader run (rc 0 on a NOT SCORED stand-in), its two outputs the only new files; R2 uncommitted 16, not run; R3 no M1 line 16; R4 E183's gate 0, the reader's rc 1 (no reduction) printed, nothing written; R5 not a data dir 10"

step "L1. step 2 v4 passes; then the upstream gains a commit rewriting the launch step with its line (the lab moved); v4 again refuses"
prep5 L1; v4 L1; ra=$?
echo "# desk test L1" >> "$H/$E5/rb/s11_a3_launch_e185_v2.sh"
h=$(cd "$H" && shasum -a 256 "$E5/rb/s11_a3_launch_e185_v2.sh")
awk -v h="$h" -v p="$E5/rb/s11_a3_launch_e185_v2.sh" '$2 == p {print h; next} {print}' "$H/$E5/SHA256SUMS-e185-kit-note1" > "$S/l1"; cp "$S/l1" "$H/$E5/SHA256SUMS-e185-kit-note1"
awk -v h="$h" -v p="$E5/rb/s11_a3_launch_e185_v2.sh" '$2 == p {print h; next} {print}' "$H/$E5/SHA256SUMS-e185-kit-note2" > "$S/l1b"; cp "$S/l1b" "$H/$E5/SHA256SUMS-e185-kit-note2"
gx "$H" add -A tools && gx "$H" commit -q -m "L1: the lab moved" > /dev/null 2>&1 && gx "$H" push -q origin HEAD:main > /dev/null 2>&1
v4 L1; rb=$?; stopline L1
q=$(has "pulled (" "$S/L1.txt"); moved=$([ "$(gx "$C" rev-parse HEAD)" != "$BASE" ] && echo 1 || echo 0)
reset_up; reset_clone
ok "$ra.$rb.$q.$moved" "0.16.1.1" "L1 v4 0, then the lab moves: the re-run pulls it and refuses (16)"

step "LM. the upstream gains an addition between the day-2 check's pull and step 2 v3's: v4 refuses"
echo "stand-in note (desk test LM, first)" > "$H/$E5/LM-first.md"; gx "$H" add -A tools && gx "$H" commit -q -m "LM first" > /dev/null 2>&1 && gx "$H" push -q origin HEAD:main > /dev/null 2>&1
cat > "$C/.git/hooks/post-merge" <<HOOK
#!/bin/sh
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
[ -e "$S/lm.flag" ] && exit 0
: > "$S/lm.flag"
echo "stand-in note (desk test LM, second)" > "$H/$E5/LM-second.md"
git -C "$H" -c user.name=day2-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null add -A tools > /dev/null 2>&1
git -C "$H" -c user.name=day2-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null commit -q -m "LM second" > /dev/null 2>&1
git -C "$H" -c core.hooksPath=/dev/null push -q origin HEAD:main > /dev/null 2>&1
exit 0
HOOK
chmod +x "$C/.git/hooks/post-merge"; rm -f "$S/lm.flag"
prep5 LM; v4 LM; rm_=$?; stopline LM
q=$(has "the lab clone moved during step 2 v3" "$S/LM.txt"); fl=$([ -e "$S/lm.flag" ] && echo 1 || echo 0)
rm -f "$C/.git/hooks/post-merge" "$S/lm.flag"
reset_up; reset_clone
ok "$rm_.$q.$fl" "16.1.1" "LM the lab moved during step 2 v3: v4 16"

step "D. a diverged clone: v4 refuses, the pull not the network's"
echo "stand-in (desk test D, local)" > "$C/$E5/D-local.md"; commit_all "D local"
echo "stand-in (desk test D, upstream)" > "$H/$E5/D-up.md"; gx "$H" add -A tools && gx "$H" commit -q -m "D up" > /dev/null 2>&1 && gx "$H" push -q origin HEAD:main > /dev/null 2>&1
prep5 D; v4 D; rd=$?; stopline D
q=$(has "pull: the clone has diverged from its upstream (not the network's" "$S/D.txt")
reset_up; reset_clone
ok "$rd.$q" "16.1" "D diverged: v4 16, not the network's"

step "X. a detached HEAD: v4 refuses, the pull not the network's"
gx "$C" checkout -q --detach HEAD
prep5 X; v4 X; rx=$?; stopline X
q=$(has "pull: HEAD is detached (not the network's" "$S/X.txt")
reset_clone
ok "$rx.$q" "16.1" "X detached: v4 16, not the network's"

step "U. the upstream gone: v4 refuses, the pull the network's"
mv "$UP" "$S/up.gone"
prep5 U; v4 U; ru=$?; stopline U
q=$(has "pull: the upstream did not answer (the network's" "$S/U.txt")
mv "$S/up.gone" "$UP"
reset_clone
ok "$ru.$q" "16.1" "U upstream gone: v4 16, the network's"

step "C. coverage: every file the day's lists, E183's harness and E185's runbook pins name lies under the day-2 check's paths"
chk paths > "$S/paths.txt" 2>&1; rp=$?
"$PY" -I - "$C" "$S/paths.txt" > "$S/coverage.txt" 2>&1 <<'PY'
import json, os, sys
repo, pf = sys.argv[1], sys.argv[2]
paths = [l.strip() for l in open(pf) if l.strip()]
top = ["e185/SHA256SUMS-e185-registration", "e185/SHA256SUMS-e185-kit", "e185/rb/SHA256SUMS-rb-e185", "e185/SHA256SUMS-e185-a1",
       "e185/SHA256SUMS-e185-kit-note1", "e185/SHA256SUMS-e185-kit-note2", "e185/frozen-e185.sha256", "e185/SHA256SUMS-e185-m1",
       "m11/SHA256SUMS", "m11/SHA256SUMS-m11"] + [f"m11/SHA256SUMS-a{i}" for i in (1, 2, 3, 4, 5, 8, 9, 10)] + \
      ["m11/SHA256SUMS-score-m11"] + [f"m11/SHA256SUMS-score-m11-v{i}" for i in (2, 3, 4, 5)] + \
      ["e183/SHA256SUMS-e183-registration", "e183/SHA256SUMS-e183-kit", "e183/SHA256SUMS-e183-note1", "e183/SHA256SUMS-e183-brief",
       "e183/SHA256SUMS-e183-m1"]
beside = ["m11/SHA256SUMS-a6", "m11/SHA256SUMS-a7", "footing-law/SHA256SUMS", "footing-law/SHA256SUMS-note1"]
named = set()
for L in top + beside:
    rel = "tools/claims-v3/" + L
    named.add(rel)
    for line in open(os.path.join(repo, rel)):
        parts = line.split()
        if len(parts) < 2 or parts[1].startswith("build/"):
            continue
        p = parts[1].lstrip("*")
        named.add(os.path.normpath(os.path.join(os.path.dirname(rel), p)) if L in beside else os.path.normpath(p))
h = json.load(open(os.path.join(repo, "tools/claims-v3/e183/harness-e183.json")))
named |= set(h["files"]) | set(h["build_inputs"])
rb = open(os.path.join(repo, "tools/claims-v3/e185/rb/rb_common_e185.sh")).read()
for p in ("q141k-runbook/v3.1/rb_run.py", "q141k-runbook/v3.1/nopath_q142s.py", "q141k-runbook/v3.1/ccdone_q142s.py", "e164/scrub_etwho_e164.py"):
    assert p.split("/")[-1] in rb
    named.add("tools/claims-v3/" + p)
dirs = [p for p in paths if os.path.isdir(os.path.join(repo, p))]
miss = sorted(p for p in named if p not in paths and not any(p.startswith(d + "/") for d in dirs))
print(f"named {len(named)}; the check's paths {len(paths)} ({len(dirs)} directories); not covered {len(miss)}")
for m in miss[:20]:
    print("  NOT COVERED", m)
PY
cat "$S/coverage.txt"
q=$(has "not covered 0" "$S/coverage.txt")
ok "$rp.$q" "0.1" "C every named file under the day-2 check's paths"

step "Z. nothing the test started is left running"
left=$(pgrep -f "$S/clone" 2>/dev/null | grep -c .)
echo "processes under the scratch clone: $left"
ok "$left" 0 "Z nothing left running"

echo
echo "calls to any box by the stand-ins: $(grep -c . "$S/calls.log"); lock lines: $(grep -c . "$RB_LOCK"); elapsed $(( $(date +%s) - t_begin )) s"
echo "SELFTEST-DAY2-V1 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL), $npass of $ncase"
exit "$fail"
