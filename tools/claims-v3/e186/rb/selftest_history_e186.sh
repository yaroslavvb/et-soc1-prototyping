#!/bin/bash
# E186 (Q158, the kit): the desk test of rb/check_history_e186.py (the history check and note M1's reader gate), on the lab's own history:
# a sparse local clone of the lab clone (git clone --local --no-checkout, then the directories E186's paths lie in), with every file of
# tools/claims-v3/e186/ as the lab tree holds it committed on top (the kit's commit, re-made where the kit is not yet committed). It never
# writes in the lab clone, never pushes, and makes no network, device or box call.
#
#   bash tools/claims-v3/e186/rb/selftest_history_e186.sh <scratch dir>     (outside the lab clone; it is emptied first)
#
# Cases (each on the kit's commit, reset after it):
#   T0  the intact tree: HISTORY OK, with the files added since E186's registration (the anchor) named by count, none shadowing;
#   T1  a kit file and its line in the kit's list rewritten together and committed: the kit's list still reads every entry OK at its count
#       (the count-only pin passes it: verify-d2b's fault 2 in E186's form), and the history check refuses it, naming both files;
#   T2  the card lane's brief edited and committed: refused, naming it (verify-d2b's fault 3 in E186's form);
#   T3  a committed json.py beside E186's scripts: refused, a module the system python finds;
#   T4  a committed copy of score_e186.py in M12's directory: refused, a module name two of E186's directories share;
#   T5  an untracked file in the workload's directory: refused, an uncommitted change on E186's paths;
#   T6  a committed rename of a file E182's lists name: refused (R);
#   T7  note M1's reader edited with its line in note M1's list, committed: the tree check passes and reports both (M1 is never a gate
#       there); step 11's M1 gate refuses (M1-NOT-RUN, 16) and the reader never runs (no arm-m1 output);
#   T8  the M1 gate on the intact tree: with no scored file, M1-NOT-RUN (16); with a stand-in scored file ("{}"), the reader runs and
#       refuses it (M1-READER-REFUSED with the reader's own rc; the checker exits 2) and nothing else in the data directory changes;
#   T9  an anchor HEAD does not descend from: refused (ancestry).
# SPDX-License-Identifier: Apache-2.0
set -u
S=${1:?usage: selftest_history_e186.sh <scratch dir>}
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
case "$(cd "$(dirname "$S")" 2>/dev/null && pwd)/" in "$SRC"/*) echo "the scratch dir is inside the lab clone: refusing"; exit 2 ;; esac
rm -rf "${S:?}"
mkdir -p "$S" || exit 2
S=$(cd "$S" && pwd)
C=$S/clone
CK="tools/claims-v3/e186/rb/check_history_e186.py"
pass=0; total=0; fail=0
step() { echo; echo "== $*"; }
ok() { total=$((total + 1)); if [ "$1" = "$2" ]; then pass=$((pass + 1)); echo "-> PASS ($3)"; else fail=1; echo "-> FAIL ($3): read $1, wanted $2"; fi; }
has() { grep -c -F -- "$1" "$2" 2>/dev/null | head -1; }
san() { sed -e "s#$SRC#<repo>#g" -e "s#$S#<scratch>#g"; }
G="git -C $C -c user.name=e186-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
chk() { ( cd "$C" && /usr/bin/python3 -I -B "$CK" "$@" ); }

# the clone: E186's paths' directories from the lab tree's own reading of them (the checker's paths mode, read only)
( cd "$SRC" && /usr/bin/python3 -I -B "$CK" paths ) > "$S/paths.txt" || { echo "the checker's paths mode failed in the lab tree"; exit 2; }
cones=$(awk -F/ '$1 == "tools" && $2 == "claims-v3" { next } $1 == "workloads" { next } { sub("/[^/]*$", ""); print }' "$S/paths.txt" | sort -u | tr '\n' ' ')
git clone -q --local --no-checkout "$SRC" "$C" || { echo "the clone failed"; exit 2; }
$G sparse-checkout set --cone tools/claims-v3 workloads/sparsity $cones || { echo "the sparse checkout failed"; exit 2; }
$G checkout -q "$(git -C "$SRC" rev-parse --abbrev-ref HEAD)" || { echo "the checkout failed"; exit 2; }
$G remote remove origin
( cd "$SRC" && find tools/claims-v3/e186 -type f ! -path '*/__pycache__/*' ) | while IFS= read -r f; do mkdir -p "$C/$(dirname "$f")"; cp -p "$SRC/$f" "$C/$f"; done
$G add -A tools/claims-v3/e186
if [ -n "$($G status --porcelain -- tools/claims-v3/e186)" ]; then $G commit -q -m "desk test: the kit's files as the lab tree holds them"; fi
K=$($G rev-parse HEAD)
reset() { $G reset -q --hard "$K"; $G clean -q -f -d -- tools/claims-v3 workloads/sparsity; }
echo "clone: $($G ls-files | wc -l | tr -d ' ') files tracked, $(grep -c . "$S/paths.txt") of E186's paths; the kit's commit $($G log -1 --format=%h); the lab's HEAD $(git -C "$SRC" log -1 --format=%h)"

step "T0. the intact tree"
chk tree > "$S/t0.txt" 2>&1; r0=$?; cat "$S/t0.txt" | san | cut -c1-400
n0=$(grep -c . "$C/tools/claims-v3/e186/SHA256SUMS-e186-kit")
ok0=$( cd "$C" && shasum -a 256 -c tools/claims-v3/e186/SHA256SUMS-e186-kit 2>/dev/null | grep -c ': OK$' )
echo "the kit's list on the intact tree: $ok0 of $n0 entries OK"
ok "$r0.$(has 'HISTORY OK: ' "$S/t0.txt").$(has 'none a shadowing module' "$S/t0.txt")" "0.1.1" "T0 the intact tree: HISTORY OK, no change but an addition since the anchor, none shadowing, nothing uncommitted"

step "T1. a kit file and its line in the kit's list rewritten together, committed"
f=tools/claims-v3/e186/score_e186.py
printf '\n# a desk-test edit\n' >> "$C/$f"
h=$(shasum -a 256 "$C/$f" | cut -d' ' -f1)
sed -i '' -e "s#^[0-9a-f]*  $f\$#$h  $f#" "$C/tools/claims-v3/e186/SHA256SUMS-e186-kit"
$G commit -q -am "desk test: score_e186.py and its kit-list line rewritten together"
n=$(grep -c . "$C/tools/claims-v3/e186/SHA256SUMS-e186-kit")
nok=$( cd "$C" && shasum -a 256 -c tools/claims-v3/e186/SHA256SUMS-e186-kit 2>/dev/null | grep -c ': OK$' )
chk tree > "$S/t1.txt" 2>&1; r1=$?; cat "$S/t1.txt" | san | cut -c1-500
ok "$([ "$nok.$n" = "$ok0.$n0" ] && echo 1 || echo 0).$r1.$(has "M $f" "$S/t1.txt").$(has 'M tools/claims-v3/e186/SHA256SUMS-e186-kit' "$S/t1.txt")" "1.16.1.1" \
  "T1 the kit's list reads as on the intact tree ($nok of $n OK, its count kept: the count-only pin passes it); the history check refuses (16), naming the file and the list"
reset

step "T2. the card lane's brief edited, committed"
printf '\nA desk-test line.\n' >> "$C/tools/claims-v3/e186/KIT-BRIEF.md"
$G commit -q -am "desk test: the brief edited"
chk tree > "$S/t2.txt" 2>&1; r2=$?; cat "$S/t2.txt" | san | cut -c1-400
ok "$r2.$(has 'M tools/claims-v3/e186/KIT-BRIEF.md' "$S/t2.txt")" "16.1" "T2 a committed change to the brief is refused (16), naming it"
reset

step "T3. a committed json.py beside E186's scripts"
printf 'raise SystemExit("a planted module")\n' > "$C/tools/claims-v3/e186/json.py"
$G add tools/claims-v3/e186/json.py && $G commit -q -m "desk test: a planted json.py"
chk tree > "$S/t3.txt" 2>&1; r3=$?; cat "$S/t3.txt" | san | cut -c1-400
ok "$r3.$(has "shadows the module 'json'" "$S/t3.txt")" "16.1" "T3 an added module the system python finds is refused (16)"
reset

step "T4. a committed copy of score_e186.py in M12's directory"
cp -p "$C/tools/claims-v3/e186/score_e186.py" "$C/tools/claims-v3/m12/score_e186.py"
$G add tools/claims-v3/m12/score_e186.py && $G commit -q -m "desk test: a module name two directories share"
chk tree > "$S/t4.txt" 2>&1; r4=$?; cat "$S/t4.txt" | san | cut -c1-400
ok "$r4.$(has "its module name 'score_e186' is also" "$S/t4.txt")" "16.1" "T4 an added module whose name another of E186's modules has is refused (16)"
reset

step "T5. an untracked file in the workload's directory"
w=$(cd "$C" && git ls-files workloads/sparsity | head -1)
printf 'x\n' > "$C/$(dirname "$w")/desktest-untracked.txt"
chk tree > "$S/t5.txt" 2>&1; r5=$?; cat "$S/t5.txt" | san | cut -c1-400
ok "$r5.$(has 'status: 1 uncommitted change' "$S/t5.txt")" "16.1" "T5 an untracked file on E186's paths is refused (16)"
reset

step "T6. a committed rename of a file E182's lists name"
f6=tools/claims-v3/e182/e182_stats.py
$G mv "$f6" "$f6.renamed" && $G commit -q -m "desk test: a rename"
chk tree > "$S/t6.txt" 2>&1; r6=$?; cat "$S/t6.txt" | san | cut -c1-400
ok "$r6.$(has 'history: ' "$S/t6.txt").$(has "$f6" "$S/t6.txt")" "16.1.1" "T6 a committed rename is refused (16), naming the file"
reset

step "T7. note M1's reader and its line in note M1's list rewritten together, committed"
f7=tools/claims-v3/e186/arm_m1_read_e186.py
printf '\n# a desk-test edit\n' >> "$C/$f7"
h=$(shasum -a 256 "$C/$f7" | cut -d' ' -f1)
sed -i '' -e "s#^[0-9a-f]*  $f7\$#$h  $f7#" "$C/tools/claims-v3/e186/SHA256SUMS-e186-m1"
$G commit -q -am "desk test: note M1's reader and its list line rewritten together"
chk tree > "$S/t7a.txt" 2>&1; r7a=$?; cat "$S/t7a.txt" | san | cut -c1-400
mkdir -p "$S/data7"; printf '{}\n' > "$S/data7/scored-e186.json"
chk m1 --data "$S/data7" > "$S/t7b.txt" 2>&1; r7b=$?; cat "$S/t7b.txt" | san | cut -c1-400
nout=$(ls "$S/data7" | grep -c '^arm-m1-e186')
ok "$r7a.$(has "note M1's files: 2 changed" "$S/t7a.txt").$r7b.$(has 'M1-NOT-RUN ' "$S/t7b.txt").$(has "own bytes differ from the pin" "$S/t7b.txt").$nout" "0.1.16.1.1.0" \
  "T7 the tree check passes and reports note M1's two files; the M1 gate refuses (16, its list's bytes) and the reader never ran"
reset

step "T8. the M1 gate on the intact tree: no scored file; then a stand-in scored file"
mkdir -p "$S/data8a" "$S/data8b"; printf 'a file the reader must leave alone\n' > "$S/data8b/results-e186.md"; printf '{}\n' > "$S/data8b/scored-e186.json"
chk m1 --data "$S/data8a" > "$S/t8a.txt" 2>&1; r8a=$?; cat "$S/t8a.txt" | san | cut -c1-300
before=$(cd "$S/data8b" && shasum -a 256 results-e186.md scored-e186.json)
chk m1 --data "$S/data8b" > "$S/t8b.txt" 2>&1; r8b=$?; tail -3 "$S/t8b.txt" | san | cut -c1-300
after=$(cd "$S/data8b" && shasum -a 256 results-e186.md scored-e186.json)
ok "$r8a.$(has 'M1-NOT-RUN ' "$S/t8a.txt").$r8b.$(has 'M1-READER-REFUSED rc ' "$S/t8b.txt").$(has 'M1-WROTE-OTHER' "$S/t8b.txt").$([ "$before" = "$after" ] && echo 1 || echo 0)" "16.1.2.1.0.1" \
  "T8 no scored file: M1-NOT-RUN (16); a stand-in: the reader ran and refused it (the checker 2), nothing else in the data directory changed"

step "T9. an anchor HEAD does not descend from"
$G checkout -q -b desktest-side && $G commit -q --allow-empty -m "desk test: a side commit" && side=$($G rev-parse HEAD) && $G checkout -q - && $G branch -q -D desktest-side
chk tree --anchor "$side" > "$S/t9.txt" 2>&1; r9=$?; cat "$S/t9.txt" | san | cut -c1-300
ok "$r9.$(has 'ancestry (HEAD does not descend from' "$S/t9.txt")" "16.1" "T9 refused (16): ancestry"

echo
[ -z "$(find "$SRC/tools/claims-v3/e186" -name __pycache__ -print -quit)" ] || echo "note: a __pycache__ appeared in the lab tree"
if [ "$fail" -eq 0 ] && [ "$pass" -eq "$total" ]; then echo "SELFTEST-HISTORY-E186 $pass of $total PASS"; exit 0; fi
echo "SELFTEST-HISTORY-E186 FAIL: $pass of $total"; exit 1
