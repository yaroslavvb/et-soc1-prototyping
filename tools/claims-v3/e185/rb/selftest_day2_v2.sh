#!/usr/bin/env bash
# E185 and E183, day 2: the desk test of the day-2 check v2 (rb/check_day2_v2.py), E185's step 2 v5 (rb/s03_desk_e185_v5.sh), E183's step 2
# v4 (../../e183/rb/s03_desk_e183_v4.sh) and their dry listings (E185's kit dated note 4, E183's kit dated note 3). It is
# selftest_day2_v1.sh's form (1e74546a, which stays as committed): a SCRATCH CLONE, shared and sparse (tools/, workloads/, rtl-sim's
# fma_toggle_v2 and the data directories the day's 47 lists name), of a local bare upstream that is itself a shared clone of the repository
# this file sits in, with the working E183 and E185 files committed over its HEAD and pushed to the upstream; a helper clone makes "the lab
# moved" cases. Stand-in ssh, rsync and scp first on PATH log any call and refuse it; no step here makes one. Every case that changes a
# file commits it in the clone (or leaves it untracked where the case says so) and is reset after. The cases (verify-fx's codes where it
# made them):
#   A   the dry listings: E185's v5 and E183's v4 exit 0 with no call; E185's lists step 2 v5 twice, the look before the post, step 14
#       after the second step 2, and the M1 gate v2 after step 14; E183's lists step 2 v4, the look before the post, and its M1 gate v2;
#   K   no window, then a window written on another day: E185 v5 10 and E183 v4 10 each time, before the day-2 check (no call, no pull);
#   P0  the intact clone: the check v2 0 and v1 0; E185 v5 0 (v2 OK, then v4's v1 OK and v3's M1 line 21 of 21); E183 v4 0; E185 v4 and
#       E183 v3 each 0 (the new files break none);
#   fault 1, each committed, v1 alone still 0 (the fault, re-made) and v2 16:
#   L3  M11's imported tools/claims-v3/hpl/surface_hpl.py edited: also E185 v5 16 and E183 v4 16, where E185's v4 and E183's v3 alone
#       read 0 (the fault, re-made at the step);
#   L4  E78's committed runs.csv (opened by the scorer) edited;
#   L5  tools/claims-v3/ccheck/ccheck.py (the collector's check of C) edited;
#   L2  M5's fit_m5.py (imported by M11's scorer through M10's code) edited together with its line in M10's SHA256SUMS (a list the
#       scorer opens, outside v1's perimeter): v2 reads that list at its own bytes;
#   E1  E181's committed measured-pass marks (score_e185.sh's own input) edited;
#   A2  rtl-sim/fma_toggle_v2/accum.c (read by the check of C) edited;
#   S7  an added tools/claims-v3/kspeed/e83/statistics.py (M11's scorer puts kspeed/e83 on sys.path): shadowing;
#   CL  kspeed/e83/predict_e83.py edited together with its line in this note's closure list;
#   fault 2, untracked (never committed), v1 alone still 0 and v2 16, except U6:
#   U3  an untracked tools/claims-v3/e164/json.py (beside E164's scrubber, which step 14 runs);
#   U5  an untracked tools/claims-v3/hpl/statistics.py;
#   U7  an untracked package tools/claims-v3/e164/json/__init__.py;
#   U8  an untracked extension module tools/claims-v3/hpl/statistics.cpython-39-darwin.so;
#   U6  an untracked working note tools/claims-v3/hpl/notes.md: v2 0 (only modules are refused outside the core directories), counted;
#   W   an untracked working note under e183 (a core directory): E183 v4 16 and E185 v5 16 (the status read; the brief's "writes or commits");
#   B   rb/check_day2_v1.py changed and not committed: v2 16 before any read (v1 not at its committed bytes);
#   R1  the M1 gate v2 for E185 after a committed stand-in data directory, with step 2's M1 line in E185's RB_OUT: 0, the reader run (rc 0),
#       its two outputs the only new files;
#   R2  the same with the data directory not committed: 16, the reader not run;
#   R4  the M1 gate v2 for E183 after a committed stand-in data directory with no reduction: 0, the reader's rc 1 printed, nothing written;
#   R6  the M1 gate v2 for E185 with L3's change committed: 16, the reader not run (v1's gate 0: the fault, re-made);
#   LM  the upstream gains an addition between the check v2's pull and step 2 v4's (a hook in the clone): E185 v5 16, "moved during step 2 v4";
#   U   the upstream gone: E185 v5 16, the pull "the network's";
#   C   coverage: every file the day's 47 lists, E183's harness and E185's runbook pins name lies under v2's paths, every one of v1's paths
#       too, and the closure list's 168 files;
#   Z   nothing the test started is left running.
#
#   bash tools/claims-v3/e185/rb/selftest_day2_v2.sh <scratch dir outside the repository> > <log>
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
L=$SRC/tools/claims-v3
NEED=$( { cat "$L"/m11/SHA256SUMS "$L"/m11/SHA256SUMS-m11 "$L"/m11/SHA256SUMS-a* "$L"/m11/SHA256SUMS-score-m11* "$L"/m11/SHA256SUMS-h2-* \
  "$L"/footing-law/SHA256SUMS* "$L"/e185/SHA256SUMS-e185-* "$L"/e185/rb/SHA256SUMS-rb-e185 "$L"/e185/rb/SHA256SUMS-day2-closure-v2 \
  "$L"/e185/frozen-e185.sha256 "$L"/e183/SHA256SUMS-e183-* "$L"/m10/SHA256SUMS "$L"/p8-600/SHA256SUMS* \
  "$L"/q141k-runbook/k6/SHA256SUMS-drivers-v3 "$SRC"/docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS \
  "$SRC"/docs/reports/data/2026-11-05-q142x-pool8-freeze/SHA256SUMS
  echo docs/reports/data/2026-11-05-q142p-pool8-predictor docs/reports/data/2026-11-05-q142x-pool8-freeze docs/reports/data/2026-11-05-q145a-a3-idle-floor; } |
  grep -oE '(docs/reports/data|rtl-sim)/[^/ ]+' | LC_ALL=C sort -u)
git clone -q --bare --shared "$SRC" "$UP" || { echo "the upstream failed"; exit 2; }
gx() { local d=$1; shift; git -C "$d" -c user.name=day2-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false "$@"; }
for k in "$C" "$H"; do
  git clone -q --shared --no-checkout "$UP" "$k" || { echo "a clone failed"; exit 2; }
  gx "$k" sparse-checkout set tools workloads $NEED "$D5" "$D3" > /dev/null 2>&1 || { echo "the sparse checkout failed"; exit 2; }
  gx "$k" checkout -q || { echo "the checkout failed"; exit 2; }
done
rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/e185/" "$C/tools/claims-v3/e185/"
rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/e183/" "$C/tools/claims-v3/e183/"
gx "$C" add -A tools/claims-v3/e185 tools/claims-v3/e183 && gx "$C" commit -q -m "day-2 desk test v2: the working E183 and E185 files" > /dev/null 2>&1
gx "$C" push -q origin HEAD:main > /dev/null 2>&1 || { echo "the push to the upstream failed"; exit 2; }
gx "$H" pull -q --ff-only > /dev/null 2>&1 || { echo "the helper's pull failed"; exit 2; }
BASE=$(gx "$C" rev-parse HEAD)
echo "scratch clone: shared and sparse ($(echo "$NEED" | grep -c .) data and bench directories the lists name), HEAD the lab clone's $(gx "$C" rev-parse --short HEAD~1) with the working E183 and E185 files committed over it ($(gx "$C" show --stat --format= HEAD | tail -n 1 | sed 's/^ *//')); a local bare upstream and a helper clone of it"
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "STAND-IN %s: refused (step 2 reaches no box)" >&2\nexit 97\n' "$n" "$S/calls.log" "$n" > "$BIN/$n"; done
chmod +x "$BIN"/*
export PATH="$BIN:$PATH" RB_REPO="$C" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$RB_LOCK"
R5=$C/tools/claims-v3/e185/rb; R3=$C/tools/claims-v3/e183/rb; E5=tools/claims-v3/e185; E3=tools/claims-v3/e183; T3=tools/claims-v3
prep5() { mkdir -p "$S/out/$1"; RB_OUT="$S/out/$1" bash "$R5/s02_window_e185.sh" "$WDAY" 23:58 23:59 > /dev/null 2>&1; }
prep3() { mkdir -p "$S/out/$1"; RB_OUT="$S/out/$1" bash "$R3/s02_window_e183.sh" "$WDAY" 23:58 23:59 > /dev/null 2>&1; }
v5() { RB_OUT="$S/out/$1" bash "$R5/s03_desk_e185_v5.sh" > "$S/$1.txt" 2>&1; }
v4() { RB_OUT="$S/out/$1" bash "$R5/s03_desk_e185_v4.sh" > "$S/$1.txt" 2>&1; }
e4() { RB_OUT="$S/out/$1" bash "$R3/s03_desk_e183_v4.sh" > "$S/$1.txt" 2>&1; }
e3() { RB_OUT="$S/out/$1" bash "$R3/s03_desk_e183_v3.sh" > "$S/$1.txt" 2>&1; }
c2() { "$PY" -I -B "$R5/check_day2_v2.py" "$@"; }
c1() { "$PY" -I -B "$R5/check_day2_v1.py" "$@"; }
reset_clone() { gx "$C" checkout -q main 2>/dev/null; gx "$C" reset -q --hard "$BASE"; gx "$C" clean -q -fdx -- tools workloads docs rtl-sim > /dev/null 2>&1; }
reset_up() { git -C "$UP" update-ref refs/heads/main "$BASE"; gx "$H" fetch -q origin; gx "$H" reset -q --hard "$BASE"; gx "$C" fetch -q origin; }
commit_all() {  # every change under tools/, workloads/ and rtl-sim/, and the stand-in data directories where a case made them
  local d extra=()
  for d in "$D5" "$D3" docs/reports/data/2026-10-31-e78-kinds-energy-matrix docs/reports/data/2026-11-06-e181-m11-session2-aifoundry3 \
           docs/reports/data/2026-11-01-q133b-power-model; do [ -d "$C/$d" ] && extra+=("$d"); done
  gx "$C" add -A tools workloads rtl-sim ${extra[@]+"${extra[@]}"} && gx "$C" commit -q -m "$1" > /dev/null 2>&1 || { echo "(the case's commit failed)"; fail=1; }
}
relist() {  # relist <list> <file>: the file's line in the list rewritten to its new hash (a file rewritten together with its line)
  local h; h=$(cd "$C" && shasum -a 256 "$2")
  awk -v h="$h" -v p="$2" '$2 == p {print h; next} {print}' "$C/$1" > "$S/relist.tmp" && cp "$S/relist.tmp" "$C/$1"
}
stopline() {  # the step's own last word: its first STOP line, else its last desk-check line (the outer step's)
  if grep -q 'STOP' "$S/$1.txt"; then grep -m1 'STOP' "$S/$1.txt" | san
  else grep -E 'desk check v[0-9]:' "$S/$1.txt" | tail -n 1 | sed 's/; october-forecast-model note M1 .*//' | san; fi
}
pair() {  # pair <case>: v1 and v2 tree checks on the clone as it is (no pull): "<v1 rc>.<v2 rc>"
  c1 tree > "$S/$1-v1.txt" 2>&1; local a=$?
  c2 tree > "$S/$1-v2.txt" 2>&1; local b=$?
  grep -m1 'STOP' "$S/$1-v2.txt" | san
  echo "$a.$b"
}
cd "$C" || exit 2

step "A. the dry listings: E185's v5 and E183's v4, every step exiting 0 with no call, in their order"
: > "$S/calls.log"
bash "$R5/list_steps_e185_v5.sh" "$S/dry5" > "$S/dry-listing-v5.txt" 2>&1; ra=$?
bash "$R3/list_steps_e183_v4.sh" "$S/dry3" > "$S/dry-listing-e183-v4.txt" 2>&1; rb=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing-v5.txt"; tail -n 1 "$S/dry-listing-e183-v4.txt"
o5=$(awk '/^################ s05_look_e185.sh aifoundry3$/ {l=NR} /^################ step 4: the day.s one post/ {p=NR}
          /^################ s03_desk_e185_v5.sh$/ {k++; d[k]=NR} /^################ s22_collect_e185_v2.sh$/ {c=NR} /check_day2_v2.py m1 e185/ {m=NR}
          END {print ((l > 0 && p > l) ? "look-first" : "POST-FIRST") "." k "." ((k == 2 && c > d[2] && d[2] > p) ? "14-after" : "ORDER") "." ((m > c) ? "m1-after" : "M1")}' "$S/dry-listing-v5.txt")
o3=$(awk '/s03_desk_e183_v4.sh/ && /^################/ {k++} /k6\/s05_look_k6.sh aifoundry3$/ {l=NR} /the day.s one post, made AFTER/ {p=NR}
          /s22_collect_e183_v2.sh/ && /^################/ {c=NR} /check_day2_v2.py m1 e183/ {m=NR}
          END {print k "." ((l > 0 && p > l) ? "look-first" : "POST-FIRST") "." ((m > c) ? "m1-after" : "M1")}' "$S/dry-listing-e183-v4.txt")
echo "calls: $n; E185 $o5; E183 $o3"
ok "$ra.$rb.$n.$o5.$o3" "0.0.0.look-first.2.14-after.m1-after.1.look-first.m1-after" "A the dry listings: 0 failing, no call, the look before the post, E185's step 2 v5 twice with step 14 after the second, each M1 gate v2 after its collection"

step "K. no window, then a window written on another day: refused before the day-2 check"
: > "$S/calls.log"
mkdir -p "$S/out/K1" "$S/out/K3"; v5 K1; k1=$?; stopline K1; e4 K3; k3=$?; stopline K3
prep5 K2; touch -t "$(date -v-1d +%Y%m%d%H%M)" "$S/out/K2/window.env"; v5 K2; k2=$?; stopline K2
prep3 K4; touch -t "$(date -v-1d +%Y%m%d%H%M)" "$S/out/K4/window.env"; e4 K4; k4=$?; stopline K4
nchk=$(cat "$S/out/K1/runbook.log" "$S/out/K2/runbook.log" "$S/out/K3/runbook.log" "$S/out/K4/runbook.log" 2>/dev/null | grep -c 'day-2 check')
n=$(grep -c . "$S/calls.log")
ok "$k1-$k2-$k3-$k4-$nchk-$n" "10-10-10-10-0-0" "K E185 v5 and E183 v4: 10 without a window and 10 with another day's, the day-2 check never reached, no call"

step "P0. the intact clone: the checks v2 and v1, E185 v5, E183 v4, and the earlier step 2s"
c2 tree > "$S/P0c.txt" 2>&1; pc=$?; grep -E 'DAY2-CHECK|the day.s paths|untracked:' "$S/P0c.txt" | san
c1 tree > "$S/P0c1.txt" 2>&1; pc1=$?
prep5 P0; v5 P0; p5=$?; stopline P0
prep3 P0e4; e4 P0e4; pe4=$?; stopline P0e4
prep5 P0v4; v4 P0v4; p4=$?; prep3 P0e3; e3 P0e3; pe3=$?
base_adds=$(sed -nE 's/.* ([0-9]+) file\(s\) added since 6860643c.*/\1/p' "$S/P0c.txt" | head -n 1); echo "  additions since 6860643c in v2's directories at the clone's HEAD: $base_adds"
hd=$(gx "$C" rev-parse --short=12 HEAD)
q=$(has "DAY2-CHECK-V2 OK at $hd" "$S/P0.txt"); q1=$(has "DAY2-CHECK OK at $hd" "$S/P0.txt")
q2=$(has "october-forecast-model note M1 present, its list 21 of 21 at its pinned bytes" "$S/P0.txt")
echo "  E185 v4 alone $p4, E183 v3 alone $pe3"
ok "$pc.$pc1.$p5.$q.$q1.$q2.$pe4.$p4.$pe3" "0.0.0.1.1.1.0.0.0" "P0 v2 0 and v1 0; E185 v5 0 (v2 OK at HEAD, v4's v1 OK, v3's M1 line 21 of 21); E183 v4 0; E185 v4 and E183 v3 each 0"

step "L3. M11's imported hpl/surface_hpl.py edited and committed: v1 passes (the fault), v2, E185 v5 and E183 v4 refuse"
echo "# desk test L3" >> "$C/$T3/hpl/surface_hpl.py"; commit_all "L3"
r=$(pair L3); echo "  v1.v2 $r"
q=$(has "M $T3/hpl/surface_hpl.py" "$S/L3-v2.txt"); q2=$(has "SHA256SUMS-day2-closure-v2 (1 entry not OK: $T3/hpl/surface_hpl.py)" "$S/L3-v2.txt")
prep5 L3v5; v5 L3v5; r5=$?; prep3 L3e4; e4 L3e4; r3=$?
prep5 L3v4; v4 L3v4; r4=$?; prep3 L3e3; e3 L3e3; r33=$?
reset_clone
ok "$(echo "$r" | tail -n 1).$q.$q2.$r5.$r3.$r4.$r33" "0.16.1.1.16.16.0.0" "L3 v1 0 (the fault, re-made); v2 16 (the history and the closure list name it); E185 v5 16 and E183 v4 16, where E185 v4 and E183 v3 alone read 0"

step "L4. E78's committed runs.csv (the scorer opens it) edited and committed: v1 passes, v2 refuses"
echo "desk,test,L4" >> "$C/docs/reports/data/2026-10-31-e78-kinds-energy-matrix/runs.csv"; commit_all "L4"
r=$(pair L4); echo "  v1.v2 $r"
q=$(has "M docs/reports/data/2026-10-31-e78-kinds-energy-matrix/runs.csv" "$S/L4-v2.txt")
reset_clone
ok "$(echo "$r" | tail -n 1).$q" "0.16.1" "L4 v1 0; v2 16, the history names it"

step "L5. the check of C (ccheck.py) edited and committed: v1 passes, v2 refuses"
echo "# desk test L5" >> "$C/$T3/ccheck/ccheck.py"; commit_all "L5"
r=$(pair L5); echo "  v1.v2 $r"
q=$(has "M $T3/ccheck/ccheck.py" "$S/L5-v2.txt")
reset_clone
ok "$(echo "$r" | tail -n 1).$q" "0.16.1" "L5 v1 0; v2 16"

step "L2. M5's fit_m5.py edited together with its line in M10's SHA256SUMS (the scorer opens that list): v1 passes, v2 refuses"
M5F=docs/reports/data/2026-11-01-q133b-power-model/fit_m5.py
echo "# desk test L2" >> "$C/$M5F"; relist "$T3/m10/SHA256SUMS" "$M5F"; commit_all "L2"
r=$(pair L2); echo "  v1.v2 $r"
q=$(has "m10/SHA256SUMS (its own bytes differ from the pin)" "$S/L2-v2.txt"); q2=$(has "M $M5F" "$S/L2-v2.txt")
reset_clone
ok "$(echo "$r" | tail -n 1).$q.$q2" "0.16.1.1" "L2 v1 0 (the fault: the file and its line rewritten together); v2 16, M10's list off its own bytes and the file in the history"

step "E1. E181's committed measured-pass marks (score_e185.sh's own input) edited and committed: v1 passes, v2 refuses"
M181=docs/reports/data/2026-11-06-e181-m11-session2-aifoundry3/aifoundry3/e181/p18120/marks.jsonl
echo '{"desk_test": "E1"}' >> "$C/$M181"; commit_all "E1"
r=$(pair E1); echo "  v1.v2 $r"
q=$(has "M $M181" "$S/E1-v2.txt")
reset_clone
ok "$(echo "$r" | tail -n 1).$q" "0.16.1" "E1 v1 0; v2 16"

step "A2. the bench's accum.c (read by the check of C) edited and committed: v1 passes, v2 refuses"
echo "/* desk test A2 */" >> "$C/rtl-sim/fma_toggle_v2/accum.c"; commit_all "A2"
r=$(pair A2); echo "  v1.v2 $r"
q=$(has "M rtl-sim/fma_toggle_v2/accum.c" "$S/A2-v2.txt")
reset_clone
ok "$(echo "$r" | tail -n 1).$q" "0.16.1" "A2 v1 0; v2 16"

step "S7. an added kspeed/e83/statistics.py (on M11's scorer's sys.path), committed: v1 passes, v2 refuses (shadowing)"
echo "# desk test S7" > "$C/$T3/kspeed/e83/statistics.py"; commit_all "S7"
r=$(pair S7); echo "  v1.v2 $r"
q=$(has "$T3/kspeed/e83/statistics.py (shadows the module 'statistics'" "$S/S7-v2.txt")
reset_clone
ok "$(echo "$r" | tail -n 1).$q" "0.16.1" "S7 v1 0; v2 16, named as shadowing"

step "CL. kspeed/e83/predict_e83.py edited together with its line in the closure list: v2 refuses"
echo "# desk test CL" >> "$C/$T3/kspeed/e83/predict_e83.py"; relist "$E5/rb/SHA256SUMS-day2-closure-v2" "$T3/kspeed/e83/predict_e83.py"; commit_all "CL"
r=$(pair CL); echo "  v1.v2 $r"
q=$(has "SHA256SUMS-day2-closure-v2 (its own bytes differ from the pin)" "$S/CL-v2.txt"); q2=$(has "M $E5/rb/SHA256SUMS-day2-closure-v2" "$S/CL-v2.txt")
reset_clone
ok "$(echo "$r" | tail -n 1).$q.$q2" "16.16.1.1" "CL v1 16 (the list is in e185, a core directory) and v2 16: the closure list off its own bytes and in the history"

step "U3, U5, U7, U8. untracked modules outside the core directories: v1 passes, v2 refuses"
echo "# desk test U3" > "$C/$T3/e164/json.py"
r=$(pair U3); echo "  U3 v1.v2 $r"; u3=$(echo "$r" | tail -n 1); q3=$(has "untracked module(s) in the day's directories: $T3/e164/json.py" "$S/U3-v2.txt"); reset_clone
echo "# desk test U5" > "$C/$T3/hpl/statistics.py"
r=$(pair U5); echo "  U5 v1.v2 $r"; u5=$(echo "$r" | tail -n 1); q5=$(has "$T3/hpl/statistics.py" "$S/U5-v2.txt"); reset_clone
mkdir -p "$C/$T3/e164/json"; echo "# desk test U7" > "$C/$T3/e164/json/__init__.py"
r=$(pair U7); echo "  U7 v1.v2 $r"; u7=$(echo "$r" | tail -n 1); q7=$(has "$T3/e164/json/__init__.py" "$S/U7-v2.txt"); reset_clone
printf 'desk test U8' > "$C/$T3/hpl/statistics.cpython-39-darwin.so"
r=$(pair U8); echo "  U8 v1.v2 $r"; u8=$(echo "$r" | tail -n 1); q8=$(has "$T3/hpl/statistics.cpython-39-darwin.so" "$S/U8-v2.txt"); reset_clone
ok "$u3.$q3.$u5.$q5.$u7.$q7.$u8.$q8" "0.16.1.0.16.1.0.16.1.0.16.1" "U3 json.py, U5 statistics.py, U7 a json package, U8 an extension module: v1 0, v2 16, each named"

step "U6. an untracked working note outside the core directories: v2 passes, the file counted"
echo "desk test U6: a working note" > "$C/$T3/hpl/notes.md"
r=$(pair U6); echo "  v1.v2 $r"
q=$(has "untracked: 1 untracked file(s) in the day's" "$S/U6-v2.txt")
reset_clone
ok "$(echo "$r" | tail -n 1).$q" "0.0.1" "U6 v1 0 and v2 0 (a note is not a module), counted"

step "W. an untracked working note under e183 (a core directory): E183 v4 and E185 v5 refuse (status)"
echo "desk test W: a lane's working note" > "$C/$E3/working-note.md"
prep3 W; e4 W; rw3=$?; stopline W; prep5 Wv5; v5 Wv5; rw5=$?
q=$(has "?? $E3/working-note.md" "$S/W.txt")
reset_clone
ok "$rw3.$rw5.$q" "16.16.1" "W E183 v4 16 and E185 v5 16, the note named (an uncommitted file on the day's paths)"

step "B. rb/check_day2_v1.py changed and not committed: v2 refuses before any read"
echo "# desk test B" >> "$R5/check_day2_v1.py"
c2 tree > "$S/B.txt" 2>&1; rbv=$?; grep -m1 STOP "$S/B.txt" | san
q=$(has "rb/check_day2_v1.py is not at its committed bytes" "$S/B.txt"); q2=$(grep -c 'lists\|history' "$S/B.txt")
reset_clone
ok "$rbv.$q.$q2" "16.1.0" "B v2 16 on v1's bytes, nothing else read"

step "R. the M1 readers' gate v2"
mkdir -p "$C/$D5" "$C/$D3"; echo "stand-in data README (desk test)" > "$C/$D5/README.md"; echo "stand-in data README (desk test)" > "$C/$D3/README.md"
echo '{"E185": {"reads": "NOT SCORED (desk test stand-in)"}}' > "$C/$D5/scored-m11.json"
commit_all "R: stand-in data directories"
RBASE=$(gx "$C" rev-parse HEAD)
prep5 R1; v5 R1 > /dev/null 2>&1
c2 m1 e185 --data "$D5" --rb-out "$S/out/R1" > "$S/R1.txt" 2>&1; r1=$?; grep -E 'M1-READER|READER-RC|M1 reader outputs' "$S/R1.txt" | san
q1=$(has "M1-READER-GATE-V2 e185 OK" "$S/R1.txt"); q1b=$(has "READER-RC 0" "$S/R1.txt"); cnt1=$(gx "$C" status --porcelain --untracked-files=all | grep -c .)
gx "$C" clean -q -fdx -- docs > /dev/null 2>&1
echo x > "$C/$D5/extra-uncommitted.txt"
c2 m1 e185 --data "$D5" --rb-out "$S/out/R1" > "$S/R2.txt" 2>&1; r2=$?; grep -m1 STOP "$S/R2.txt" | san
q2=$(has "READER-RC" "$S/R2.txt")
gx "$C" clean -q -fdx -- docs > /dev/null 2>&1
c2 m1 e183 --data "$D3" > "$S/R4.txt" 2>&1; r4=$?; grep -E 'M1-READER|READER-RC|M1 reader outputs' "$S/R4.txt" | san
q4=$(has "M1-READER-GATE-V2 e183 OK" "$S/R4.txt"); q4b=$(has "READER-RC 1" "$S/R4.txt"); cnt4=$(gx "$C" status --porcelain --untracked-files=all | grep -c .)
gx "$C" clean -q -fdx -- docs > /dev/null 2>&1
echo "# desk test R6" >> "$C/$T3/hpl/surface_hpl.py"; commit_all "R6"
c1 m1 e185 --data "$D5" --rb-out "$S/out/R1" > "$S/R6v1.txt" 2>&1; r6a=$?
gx "$C" clean -q -fdx -- docs > /dev/null 2>&1
c2 m1 e185 --data "$D5" --rb-out "$S/out/R1" > "$S/R6.txt" 2>&1; r6=$?; grep -m1 STOP "$S/R6.txt" | san
q6=$(has "READER-RC" "$S/R6.txt")
reset_clone
ok "$r1.$q1.$q1b.$cnt1.$r2.$q2.$r4.$q4.$q4b.$cnt4.$r6a.$r6.$q6" "0.1.1.2.16.0.0.1.1.0.0.16.0" "R1 E185's gate v2 0, the reader run (rc 0), its two outputs the only new files; R2 uncommitted 16, not run; R4 E183's gate v2 0, the reader's rc 1 printed, nothing written; R6 a scorer module changed: v1's gate 0 (the fault), v2's 16, not run"

step "LM. the upstream gains an addition between the check v2's pull and step 2 v4's: v5 refuses"
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
prep5 LM; v5 LM; rm_=$?; stopline LM
q=$(has "the lab clone moved during step 2 v4" "$S/LM.txt"); fl=$([ -e "$S/lm.flag" ] && echo 1 || echo 0)
rm -f "$C/.git/hooks/post-merge" "$S/lm.flag"
reset_up; reset_clone
ok "$rm_.$q.$fl" "16.1.1" "LM the lab moved during step 2 v4: v5 16"

step "U. the upstream gone: v5 refuses, the pull the network's"
mv "$UP" "$S/up.gone"
prep5 U; v5 U; ru=$?; stopline U
q=$(has "pull: the upstream did not answer (the network's" "$S/U.txt")
mv "$S/up.gone" "$UP"
reset_clone
ok "$ru.$q" "16.1" "U upstream gone: v5 16, the network's"

step "C. coverage: every file the day's 47 lists, E183's harness and E185's runbook pins name lies under v2's paths, and v1's paths"
c2 paths > "$S/paths2.txt" 2>&1; rp=$?; c1 paths > "$S/paths1.txt" 2>&1; rp1=$?
"$PY" -I - "$C" "$S/paths2.txt" "$S/paths1.txt" > "$S/coverage.txt" 2>&1 <<'PY'
import importlib.util, json, os, sys
repo, pf2, pf1 = sys.argv[1], sys.argv[2], sys.argv[3]
p2 = [l.strip() for l in open(pf2) if l.strip()]
p1 = [l.strip() for l in open(pf1) if l.strip()]
spec = importlib.util.spec_from_file_location("v2", os.path.join(repo, "tools/claims-v3/e185/rb/check_day2_v2.py"))
v2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v2)
spec1 = importlib.util.spec_from_file_location("v1", os.path.join(repo, "tools/claims-v3/e185/rb/check_day2_v1.py"))
v1 = importlib.util.module_from_spec(spec1); spec1.loader.exec_module(v1)
lists = list(v1.LISTS) + list(v2.ADDED_LISTS)
named = set()
for rel, base, *_ in lists:
    named.add(rel)
    for line in open(os.path.join(repo, rel)):
        parts = line.split()
        if len(parts) < 2 or parts[1].startswith("build/"):
            continue
        p = parts[1].lstrip("*")
        named.add(os.path.normpath(os.path.join(os.path.dirname(rel), p)) if base == "beside" else os.path.normpath(p))
h = json.load(open(os.path.join(repo, "tools/claims-v3/e183/harness-e183.json")))
named |= set(h["files"]) | set(h["build_inputs"]) | set(v1.RB_PINS_FILES)
dirs = [p for p in p2 if os.path.isdir(os.path.join(repo, p))]
under = lambda p: p in p2 or any(p.startswith(d + "/") for d in dirs)
miss = sorted(p for p in named if not under(p))
miss1 = sorted(p for p in p1 if not under(p) and not os.path.isdir(os.path.join(repo, p)))
clo = [l.split()[1] for l in open(os.path.join(repo, v2.CLOSURE)) if l.strip()]
missc = [p for p in clo if not under(p)]
print(f"lists {len(lists)}; named {len(named)}; v2's paths {len(p2)} ({len(dirs)} directories); not covered {len(miss)}; "
      f"v1's paths not under v2's {len(miss1)}; the closure list {len(clo)}, not covered {len(missc)}")
for m in (miss + miss1 + missc)[:20]:
    print("  NOT COVERED", m)
PY
cat "$S/coverage.txt"
q=$(has "not covered 0; v1's paths not under v2's 0; the closure list 168, not covered 0" "$S/coverage.txt")
ok "$rp.$rp1.$q" "0.0.1" "C every named file, every one of v1's paths and the closure list's 168 under v2's paths"

step "Z. nothing the test started is left running"
left=$(pgrep -f "$S/clone" 2>/dev/null | grep -c .)
echo "processes under the scratch clone: $left"
ok "$left" 0 "Z nothing left running"

echo
echo "calls to any box by the stand-ins: $(grep -c . "$S/calls.log"); lock lines: $(grep -c . "$RB_LOCK"); elapsed $(( $(date +%s) - t_begin )) s"
echo "SELFTEST-DAY2-V2 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL), $npass of $ncase"
exit "$fail"
