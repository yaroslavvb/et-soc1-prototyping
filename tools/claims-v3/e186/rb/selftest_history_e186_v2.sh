#!/bin/bash
# E186 kit note 1 (Q158, fix-e186): the desk test of rb/check_history_e186_v2.py (v1's history check with the session scale's route in its
# perimeter; verify-e186's fault 4), on the lab's own history, in rb/selftest_history_e186.sh's form: a sparse local clone of the lab
# clone (git clone --local --no-checkout, then the directories v2's paths lie in), with every file of tools/claims-v3/e186/ as the lab tree
# holds it committed on top (kit note 1's commit, re-made where it is not yet committed). Each case runs v1 (rb/check_history_e186.py,
# unchanged) and v2 on the same tree, so it shows what v2 adds. It never writes in the lab clone, never pushes, and makes no network,
# device or box call.
#
#   bash tools/claims-v3/e186/rb/selftest_history_e186_v2.sh <scratch dir>     (outside the lab clone; it is emptied first)
#
# Cases (each on kit note 1's commit, reset after it):
#   U0  the intact tree: v1 and v2 read HISTORY OK; v2 names the six lists it adds with their counts (209, 16, 9, 68, 10, 160) and reads
#       more named files than v1;
#   U1  v1's T1 again under v2: a kit file and its line in the kit's list rewritten together, committed: both refuse (16);
#   U2  THE VERIFIER'S CASE: M10's m10.json edited with its line in M10's SHA256SUMS-a2 rewritten, committed: v1 reads HISTORY OK (the
#       hole), v2 refuses (16) naming m10.json and the list;
#   U3  a pool-8 registered input (fit_m9.py, which fit_m10 imports) edited with its line in POOL8-SHA256SUMS rewritten: v1 OK, v2 16;
#   U4  pool 8's frozen predictions for aifoundry3 (the scale's anchor features) edited with their line in the freeze's SHA256SUMS
#       rewritten: v1 OK, v2 16;
#   U5  predict_m10.py, which the scale route imports, edited with its line in M10's own SHA256SUMS (beside it) rewritten: v1 OK, v2 16;
#   U6  a committed json.py planted in M10's data directory (the directory the scale route puts first on sys.path): v1 OK, v2 refuses it
#       as a module the system python finds;
#   U7  an uncommitted edit of m10-s7.json (a file M10's SHA256SUMS-a2 names): v1 OK, v2 refuses (an uncommitted change on E186's
#       paths, named); as in v1, an untracked file outside the core directories is not read (only the files the lists name are);
#   U8  v2's m1 mode is v1's: on the intact tree with a stand-in scored file ("{}") both run the reader, which refuses it (2), and
#       nothing else in the data directory changes.
# SPDX-License-Identifier: Apache-2.0
set -u
S=${1:?usage: selftest_history_e186_v2.sh <scratch dir>}
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
case "$(cd "$(dirname "$S")" 2>/dev/null && pwd)/" in "$SRC"/*) echo "the scratch dir is inside the lab clone: refusing"; exit 2 ;; esac
rm -rf "${S:?}"
mkdir -p "$S" || exit 2
S=$(cd "$S" && pwd)
C=$S/clone
CK1="tools/claims-v3/e186/rb/check_history_e186.py"
CK2="tools/claims-v3/e186/rb/check_history_e186_v2.py"
pass=0; total=0; fail=0
step() { echo; echo "== $*"; }
ok() { total=$((total + 1)); if [ "$1" = "$2" ]; then pass=$((pass + 1)); echo "-> PASS ($3)"; else fail=1; echo "-> FAIL ($3): read $1, wanted $2"; fi; }
has() { grep -c -F -- "$1" "$2" 2>/dev/null | head -1; }
san() { sed -e "s#$SRC#<repo>#g" -e "s#$S#<scratch>#g"; }
G="git -C $C -c user.name=e186-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
c1() { ( cd "$C" && /usr/bin/python3 -I -B "$CK1" "$@" ); }
c2() { ( cd "$C" && /usr/bin/python3 -I -B "$CK2" "$@" ); }
both() { c1 tree > "$S/$1-v1.txt" 2>&1; echo $?; }
relist() {  # relist <list> <file, as the list names it> <file from the top>: the list's line for the file rewritten to its new sha256
  local l=$1 e=$2 f=$3 h
  h=$(shasum -a 256 "$C/$f" | cut -d' ' -f1)
  sed -i '' -e "s#^[0-9a-f]*  $e\$#$h  $e#" "$C/$l"
  grep -q "^$h  $e\$" "$C/$l" || echo "relist: the line for $e was not rewritten in $l"
}

( cd "$SRC" && /usr/bin/python3 -I -B "$CK2" paths ) > "$S/paths.txt" || { echo "v2's paths mode failed in the lab tree"; exit 2; }
cones=$(awk -F/ '$1 == "tools" && $2 == "claims-v3" { next } $1 == "workloads" { next } { sub("/[^/]*$", ""); print }' "$S/paths.txt" | sort -u | tr '\n' ' ')
git clone -q --local --no-checkout "$SRC" "$C" || { echo "the clone failed"; exit 2; }
$G sparse-checkout set --cone tools/claims-v3 workloads/sparsity $cones || { echo "the sparse checkout failed"; exit 2; }
$G checkout -q "$(git -C "$SRC" rev-parse --abbrev-ref HEAD)" || { echo "the checkout failed"; exit 2; }
$G remote remove origin
( cd "$SRC" && find tools/claims-v3/e186 -type f ! -path '*/__pycache__/*' ) | while IFS= read -r f; do mkdir -p "$C/$(dirname "$f")"; cp -p "$SRC/$f" "$C/$f"; done
$G add -A tools/claims-v3/e186
if [ -n "$($G status --porcelain -- tools/claims-v3/e186)" ]; then $G commit -q -m "desk test: the kit's files as the lab tree holds them"; fi
K=$($G rev-parse HEAD)
reset() { $G reset -q --hard "$K"; $G clean -q -f -d -- tools/claims-v3 workloads/sparsity docs/reports/data; }
echo "clone: $($G ls-files | wc -l | tr -d ' ') files tracked, $(grep -c . "$S/paths.txt") of v2's paths; the commit under test $($G log -1 --format=%h); the lab's HEAD $(git -C "$SRC" log -1 --format=%h)"

M10D=docs/reports/data/2026-11-04-q142m-m10
PD=docs/reports/data/2026-11-05-q142p-pool8-predictor
FZ=docs/reports/data/2026-11-05-q142x-pool8-freeze

step "U0. the intact tree"
c1 tree > "$S/u0-v1.txt" 2>&1; a=$?; c2 tree > "$S/u0-v2.txt" 2>&1; b=$?
san < "$S/u0-v1.txt" | cut -c1-300; san < "$S/u0-v2.txt" | cut -c1-700
n1=$(sed -n 's/.*directories and \([0-9]*\) named files outside them.*/\1/p' "$S/u0-v1.txt" | head -1)
n2=$(sed -n 's/.*directories and \([0-9]*\) named files outside them.*/\1/p' "$S/u0-v2.txt" | head -1)
lists=0
for x in "tools/claims-v3/m10/POOL8-SHA256SUMS 209" "$PD/SHA256SUMS 16" "$PD/SHA256SUMS-a2 9" "$M10D/SHA256SUMS 68" "$M10D/SHA256SUMS-a2 10" "$FZ/SHA256SUMS 160"; do
  lists=$((lists + $(has "$x," "$S/u0-v2.txt")))
done
ok "$a.$b.$(has 'HISTORY OK: ' "$S/u0-v1.txt").$(has 'HISTORY OK: ' "$S/u0-v2.txt").$lists.$([ "${n2:-0}" -gt "${n1:-0}" ] && echo 1 || echo 0)" "0.0.1.1.6.1" \
  "U0 the intact tree: v1 and v2 HISTORY OK; v2 adds the six lists at their counts and reads $n2 named files outside the directories (v1 $n1)"

step "U1. v1's T1 under v2: a kit file and its kit-list line rewritten together, committed"
f=tools/claims-v3/e186/score_e186.py
printf '\n# a desk-test edit\n' >> "$C/$f"
relist tools/claims-v3/e186/SHA256SUMS-e186-kit "$f" "$f"
$G commit -q -am "desk test: score_e186.py and its kit-list line rewritten together"
c1 tree > "$S/u1-v1.txt" 2>&1; a=$?; c2 tree > "$S/u1-v2.txt" 2>&1; b=$?
san < "$S/u1-v2.txt" | tail -1 | cut -c1-400
ok "$a.$b.$(has "M $f" "$S/u1-v2.txt")" "16.16.1" "U1 both refuse (16), v2 naming the file"
reset

step "U2. the verifier's case: m10.json edited with its line in M10's SHA256SUMS-a2 rewritten, committed"
printf '\n' >> "$C/$M10D/m10.json"
relist "$M10D/SHA256SUMS-a2" m10.json "$M10D/m10.json"
$G commit -q -am "desk test: m10.json and its SHA256SUMS-a2 line rewritten together"
nok=$( cd "$C/$M10D" && shasum -a 256 -c SHA256SUMS-a2 2>/dev/null | grep -c ': OK$' )
c1 tree > "$S/u2-v1.txt" 2>&1; a=$?; c2 tree > "$S/u2-v2.txt" 2>&1; b=$?
san < "$S/u2-v1.txt" | tail -1 | cut -c1-250; san < "$S/u2-v2.txt" | tail -1 | cut -c1-400
ok "$nok.$a.$b.$(has "M $M10D/m10.json" "$S/u2-v2.txt").$(has "M $M10D/SHA256SUMS-a2" "$S/u2-v2.txt")" "10.0.16.1.1" \
  "U2 M10's list still reads $nok of 10 OK; v1 HISTORY OK (the hole); v2 refuses (16), naming m10.json and its list"
reset

step "U3. a pool-8 registered input (fit_m9.py) edited with its line in POOL8-SHA256SUMS rewritten, committed"
f3=docs/reports/data/2026-11-04-q140m-m9/fit_m9.py
printf '\n# a desk-test edit\n' >> "$C/$f3"
relist tools/claims-v3/m10/POOL8-SHA256SUMS "$f3" "$f3"
$G commit -q -am "desk test: fit_m9.py and its POOL8 line rewritten together"
c1 tree > "$S/u3-v1.txt" 2>&1; a=$?; c2 tree > "$S/u3-v2.txt" 2>&1; b=$?
san < "$S/u3-v2.txt" | tail -1 | cut -c1-400
ok "$a.$b.$(has "M $f3" "$S/u3-v2.txt").$(has 'M tools/claims-v3/m10/POOL8-SHA256SUMS' "$S/u3-v2.txt")" "0.16.1.1" "U3 v1 OK; v2 refuses (16), naming the file and POOL8-SHA256SUMS"
reset

step "U4. pool 8's frozen predictions for aifoundry3 edited with their line in the freeze's SHA256SUMS rewritten, committed"
f4=tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry3.json
printf '\n' >> "$C/$f4"
relist "$FZ/SHA256SUMS" "$f4" "$f4"
$G commit -q -am "desk test: pool 8's aifoundry3 predictions and their freeze line rewritten together"
c1 tree > "$S/u4-v1.txt" 2>&1; a=$?; c2 tree > "$S/u4-v2.txt" 2>&1; b=$?
san < "$S/u4-v2.txt" | tail -1 | cut -c1-400
ok "$a.$b.$(has "M $f4" "$S/u4-v2.txt")" "0.16.1" "U4 v1 OK; v2 refuses (16), naming the predictions"
reset

step "U5. predict_m10.py edited with its line in M10's own SHA256SUMS (beside it) rewritten, committed"
printf '\n# a desk-test edit\n' >> "$C/$M10D/predict_m10.py"
relist "$M10D/SHA256SUMS" predict_m10.py "$M10D/predict_m10.py"
$G commit -q -am "desk test: predict_m10.py and its M10 list line rewritten together"
c1 tree > "$S/u5-v1.txt" 2>&1; a=$?; c2 tree > "$S/u5-v2.txt" 2>&1; b=$?
san < "$S/u5-v2.txt" | tail -1 | cut -c1-400
ok "$a.$b.$(has "M $M10D/predict_m10.py" "$S/u5-v2.txt")" "0.16.1" "U5 v1 OK; v2 refuses (16), naming predict_m10.py"
reset

step "U6. a committed json.py planted in M10's data directory"
printf 'raise SystemExit("a planted module")\n' > "$C/$M10D/json.py"
$G add "$M10D/json.py" && $G commit -q -m "desk test: a planted json.py in M10's directory"
c1 tree > "$S/u6-v1.txt" 2>&1; a=$?; c2 tree > "$S/u6-v2.txt" 2>&1; b=$?
san < "$S/u6-v2.txt" | tail -1 | cut -c1-400
ok "$a.$b.$(has "shadows the module 'json'" "$S/u6-v2.txt")" "0.16.1" "U6 v1 OK; v2 refuses (16) a module the system python finds"
reset

step "U7. an uncommitted edit of m10-s7.json (named by M10's SHA256SUMS-a2), not committed"
printf '\n' >> "$C/$M10D/m10-s7.json"
c1 tree > "$S/u7-v1.txt" 2>&1; a=$?; c2 tree > "$S/u7-v2.txt" 2>&1; b=$?
san < "$S/u7-v2.txt" | tail -1 | cut -c1-300
ok "$a.$b.$(has 'status: 1 uncommitted change' "$S/u7-v2.txt").$(has "$M10D/m10-s7.json" "$S/u7-v2.txt")" "0.16.1.1" \
  "U7 v1 OK; v2 refuses (16) an uncommitted change to a file the scale route reads, naming it"
reset

step "U8. v2's m1 mode is v1's: a stand-in scored file on the intact tree"
for v in 1 2; do
  mkdir -p "$S/data8-$v"; printf 'a file the reader must leave alone\n' > "$S/data8-$v/results-e186.md"; printf '{}\n' > "$S/data8-$v/scored-e186.json"
done
c1 m1 --data "$S/data8-1" > "$S/u8-v1.txt" 2>&1; a=$?; c2 m1 --data "$S/data8-2" > "$S/u8-v2.txt" 2>&1; b=$?
tail -1 "$S/u8-v2.txt" | san | cut -c1-200
same=$([ "$(san < "$S/u8-v1.txt" | sed -e 's#data8-1#DATA#g')" = "$(san < "$S/u8-v2.txt" | sed -e 's#data8-2#DATA#g')" ] && echo 1 || echo 0)
ok "$a.$b.$(has 'M1-READER-REFUSED rc ' "$S/u8-v2.txt").$same" "2.2.1.1" "U8 v1 and v2 read the same M1 gate: the reader ran and refused the stand-in (2), word for word"

echo
[ -z "$(find "$SRC/tools/claims-v3/e186" -name __pycache__ -print -quit)" ] || echo "note: a __pycache__ appeared in the lab tree"
if [ "$fail" -eq 0 ] && [ "$pass" -eq "$total" ]; then echo "SELFTEST-HISTORY-E186-V2 $pass of $total PASS"; exit 0; fi
echo "SELFTEST-HISTORY-E186-V2 FAIL: $pass of $total"; exit 1
