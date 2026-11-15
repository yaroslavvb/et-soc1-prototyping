#!/usr/bin/env bash
# E188 (Q182, the kit's dated note 2, KIT.md.dated-note-2.md, Sun 15 Nov 2026, before any E188 datum): E188's committed desk tests run again,
# as committed, on this desk, each read against what it should print HERE. On the Intel (macOS, /usr/bin/python3 3.9.6) every one reads as
# its committed log does. On aifoundry2 (Linux, /usr/bin/python3 3.12.3) three of them differ, for the reasons note 2 gives, and this file
# states and checks each reading:
#   - rb/selftest_rest_e188.sh, rb/selftest_rest_e188_v2.sh and dry_intel_e188.sh refuse without `gdate`: run through desk/gnudate_e188.sh
#     (GNU date as gdate, for that command only), they read 20 of 20, 32 of 32 and PASS;
#   - selftest_score_e188.py reads 18 of 20 under 3.12: its A1 (E186's scale s re-made, compared to E186's scored s to the last bit) and A2
#     (E182's train reduction re-made on E186's committed blocks, compared to trains-e186.json to the last bit) differ in their last digits;
#     run again with the built-in sum() as before 3.12 (a sitecustomize.py written at run time into a scratch directory put on PYTHONPATH,
#     which replaces sum() by plain left-to-right addition in every Python process the test starts), it reads 20 of 20: the difference is
#     3.12's compensated summation of floats, nothing else;
#   - rb/selftest_rb_e188_v2.sh reads 12 of 16 on Linux, failing exactly P1, P2-P5, P6-P7 (BSD sed's `sed -i ''` in its setup and cases;
#     step 2 v1's /usr/bin/lockf and its forecast byte check) and S1 (its grep for Homebrew's GCC): rb/selftest_rb_e188_v3.sh is its port;
#   - the others read as committed: selftest_arm_e188.py 14 of 14, selftest_stops_e188t.py 8 of 8, desktest_host_e188.sh 29 of 29,
#     desk/desktest_train_check_e188.sh 50 of 50 (here with g++-13 and clang++ 18), rb/list_steps_e188_v2.sh 19 steps, 0 non-zero.
# Run it inside the round's CPU slot and a no-device sandbox (several of these tests run built hosts). Writes only under <scratch dir>.
#   bash tools/claims-v3/e188/desk/reruns_note2_e188.sh <scratch dir outside the repository> > <log>
# Prints one line a test and RERUNS-NOTE2-E188 PASS or FAIL (<n> of <m>); exit 0 or 1.
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible here: run this inside a no-device sandbox"; exit 2; }
mkdir -p "$S" && S=$(cd "$S" && pwd)
for d in rest-v1 rest-v2 score score-sum39 arm stops host train-check dry-intel dry-listing-v2 rb-v2 sum39; do
  [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }
done
E=$SRC/tools/claims-v3/e188
OS=$(uname -s); PYV=$(/usr/bin/python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')
NEW=$(/usr/bin/python3 -c 'import sys; print(1 if sys.version_info >= (3, 12) else 0)')
ME=$(id -un)
main() {
echo "desk: $OS $(uname -m); /usr/bin/python3 $PYV; $(command -v g++-13 > /dev/null && g++-13 --version | head -n 1); $(command -v clang++ > /dev/null && clang++ --version | head -n 1)"
npass=0; ncase=0; fail=0
ok() { ncase=$((ncase + 1)); if [ "$1" = 0 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fail=1; fi; }
run() {  # run <name> <command...>: the test's log in <scratch>/<name>.log, its exit status in RC
  local n=$1; shift
  mkdir -p "$S/$n"
  ( cd "$SRC" && "$@" ) > "$S/$n.log" 2>&1; RC=$?
}
last() { grep -aE "$2" "$S/$1.log" | tail -n 1 | cut -c1-200; }
cnt() { grep -acE "$2" "$S/$1.log"; }
echo; echo "== the committed tests that refuse without gdate, through desk/gnudate_e188.sh"
run rest-v1 bash "$E/desk/gnudate_e188.sh" bash "$E/rb/selftest_rest_e188.sh" "$S/rest-v1"; echo "rc $RC: $(last rest-v1 '^SELFTEST-REST-E188 ')"
[ "$RC" -eq 0 ] && [ "$(cnt rest-v1 '^SELFTEST-REST-E188 PASS \(20 of 20\)')" = 1 ]; ok $? "rb/selftest_rest_e188.sh: 20 of 20"
run rest-v2 bash "$E/desk/gnudate_e188.sh" bash "$E/rb/selftest_rest_e188_v2.sh" "$S/rest-v2"; echo "rc $RC: $(last rest-v2 '^SELFTEST-REST-E188-V2 ')"
[ "$RC" -eq 0 ] && [ "$(cnt rest-v2 '^SELFTEST-REST-E188-V2 PASS \(32 of 32\)')" = 1 ]; ok $? "rb/selftest_rest_e188_v2.sh: 32 of 32"
run dry-intel bash "$E/desk/gnudate_e188.sh" bash "$E/dry_intel_e188.sh" "$S/dry-intel"; echo "rc $RC: $(last dry-intel '^DRY-INTEL-E188 ')"
[ "$RC" -eq 0 ] && [ "$(cnt dry-intel '^DRY-INTEL-E188 PASS')" = 1 ]; ok $? "dry_intel_e188.sh: PASS"
echo; echo "== the scorer's self-test: as committed, then with sum() as before 3.12"
run score /usr/bin/python3 -B "$E/selftest_score_e188.py" "$S/score"; echo "rc $RC: $(last score '^SELFTEST-SCORE-E188 ' | cut -c1-60)"
fails=$(grep -aE '^FAIL ' "$S/score.log" | cut -d' ' -f2 | tr '\n' ' ')
echo "its failing cases: ${fails:-none}"
mkdir -p "$S/sum39"
cat > "$S/sum39/sitecustomize.py" <<'PYEOF'
# desk only (reruns_note2_e188.sh): the built-in sum() as before Python 3.12 - plain left-to-right addition (3.12 adds floats with
# compensated summation); imported by every Python process started with this directory on PYTHONPATH (not under -I, -E or -S)
import builtins


def _sum_left_to_right(iterable, /, start=0):
    total = start
    for x in iterable:
        total = total + x
    return total


builtins.sum = _sum_left_to_right
PYEOF
run score-sum39 env PYTHONPATH="$S/sum39" /usr/bin/python3 -B "$E/selftest_score_e188.py" "$S/score-sum39"; rc39=$RC
echo "with sum() as before 3.12: rc $rc39: $(last score-sum39 '^SELFTEST-SCORE-E188 ' | cut -c1-60)"
if [ "$NEW" = 1 ]; then
  [ "$fails" = "A1 A2 " ] && [ "$(cnt score '^SELFTEST-SCORE-E188 18 of 20 ')" = 1 ] && [ "$rc39" -eq 0 ] && [ "$(cnt score-sum39 '^SELFTEST-SCORE-E188 20 of 20 PASS')" = 1 ]
  ok $? "selftest_score_e188.py under $PYV: 18 of 20, exactly A1 and A2 (last-digit equality of reductions of E186's committed data); with sum() as before 3.12, 20 of 20"
else
  [ "$RC" -eq 0 ] && [ "$(cnt score '^SELFTEST-SCORE-E188 20 of 20 PASS')" = 1 ] && [ "$rc39" -eq 0 ]; ok $? "selftest_score_e188.py under $PYV: 20 of 20, both ways"
fi
echo; echo "== the others, as committed"
run arm /usr/bin/python3 -B "$E/selftest_arm_e188.py" "$S/arm"; echo "rc $RC: $(last arm '^SELFTEST-ARM-E188 ')"
[ "$RC" -eq 0 ] && [ "$(cnt arm '^SELFTEST-ARM-E188 14 of 14 PASS')" = 1 ]; ok $? "selftest_arm_e188.py: 14 of 14"
run stops /usr/bin/python3 -B "$E/selftest_stops_e188t.py" "$S/stops"; echo "rc $RC: $(last stops '^SELFTEST-STOPS-E188T ')"
[ "$RC" -eq 0 ] && [ "$(cnt stops '^SELFTEST-STOPS-E188T 8 of 8 PASS')" = 1 ]; ok $? "selftest_stops_e188t.py: 8 of 8"
run host bash "$E/desktest_host_e188.sh" "$S/host"; echo "rc $RC: $(last host '^DESKTEST-HOST-E188 ')"
[ "$RC" -eq 0 ] && [ "$(cnt host '^DESKTEST-HOST-E188 29 of 29 PASS')" = 1 ]; ok $? "desktest_host_e188.sh: 29 of 29"
run train-check bash "$E/desk/desktest_train_check_e188.sh" "$S/train-check"; echo "rc $RC: $(last train-check '^DESKTEST-TRAIN-CHECK-E188 ')"
[ "$RC" -eq 0 ] && [ "$(cnt train-check '^DESKTEST-TRAIN-CHECK-E188 PASS \(50 of 50\)')" = 1 ]; ok $? "desk/desktest_train_check_e188.sh: 50 of 50"
run dry-listing-v2 bash "$E/rb/list_steps_e188_v2.sh" "$S/dry-listing-v2"; echo "rc $RC: $(last dry-listing-v2 '^dry listing: ')"
[ "$RC" -eq 0 ] && [ "$(cnt dry-listing-v2 '^dry listing: 19 steps listed, 0 exited non-zero$')" = 1 ]; ok $? "rb/list_steps_e188_v2.sh: 19 steps, 0 non-zero"
echo; echo "== the runbook desk test v2, as committed (its port is rb/selftest_rb_e188_v3.sh)"
run rb-v2 bash "$E/desk/gnudate_e188.sh" bash "$E/rb/selftest_rb_e188_v2.sh" "$S/rb-v2"
rbf=$(grep -aE '^-> FAIL \(' "$S/rb-v2.log" | sed -E 's/^-> FAIL \(([A-Z0-9-]+) .*/\1/' | tr '\n' ' ')
echo "rc $RC: $(last rb-v2 '^SELFTEST-RB-E188-V2 '); its failing cases: ${rbf:-none}"
if [ "$OS" = Linux ]; then
  [ "$RC" -eq 1 ] && [ "$(cnt rb-v2 '^SELFTEST-RB-E188-V2 12 of 16 FAIL')" = 1 ] && [ "$rbf" = "P1 P2-P5 P6-P7 S1 " ] && [ "$(cnt rb-v2 "^sed: can't read : No such file or directory")" -ge 1 ]
  ok $? "rb/selftest_rb_e188_v2.sh on Linux: 12 of 16, failing exactly P1, P2-P5, P6-P7 (BSD sed; step 2 v1's lockf and forecast byte check) and S1 (Homebrew's GCC)"
else
  [ "$RC" -eq 0 ] && [ "$(cnt rb-v2 '^SELFTEST-RB-E188-V2 16 of 16 PASS')" = 1 ]; ok $? "rb/selftest_rb_e188_v2.sh on the Intel: 16 of 16"
fi
echo
echo "RERUNS-NOTE2-E188 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase): E188's committed desk tests on this desk ($OS, Python $PYV), each as note 2 says it reads here"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g; s#$HOME#<home>#g; s#\\b$ME\\b#<login>#g"
exit "${PIPESTATUS[0]}"
