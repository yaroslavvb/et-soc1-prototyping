#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): THE KIT'S CHECKS, one log (logs/checks-e202.txt): the common
# module's self-check; the harness re-made and every file at its sha256; the registration's own checks (its list, the forecast and the plan
# re-made, the scorer's stand-in self-test with its stub unchanged after); the preflight (dmcmd_audit_v2 GO, every send site a READ); the
# history check's shadow names; the ledger v3 note re-made (fix-e202: v3note_e202.py --check); every shell file's syntax (bash -n) and
# every Python file's (parsed, nothing written); and that no kit file writes outside build/ on the box (the runner's and the build's own
# paths). Desk checks of code, nothing measured.
#   bash tools/claims-v3/e202/desk/checks_e202.sh <scratch dir outside the repo>
# Prints CHECKS-E202 <n> of <m> PASS or FAIL last. SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." || exit 2
S=${1:?a scratch directory outside the repository}
mkdir -p "$S"
E=tools/claims-v3/e202
n=0; m=0
ok() { m=$((m + 1)); if [ "$1" = 0 ]; then n=$((n + 1)); echo "PASS $2"; else echo "FAIL $2"; fi; }
echo "checks_e202: $(date '+%F %T %Z'); /usr/bin/python3 $(/usr/bin/python3 -c 'import sys; print(sys.version.split()[0])')"
r=$(/usr/bin/python3 -I -B $E/e202_common.py); [ "$r" = "E202-COMMON SELF-CHECK PASS" ]; ok $? "the common module's self-check: $r"
r=$(/usr/bin/python3 -I -B $E/check_e202.py --check); [ "$r" = "CHECK PASS" ]; ok $? "harness-e202.json re-made: $r"
r=$(/usr/bin/python3 -I -B $E/check_e202.py --box); case "$r" in "HARNESS OK: 30 files") true ;; *) false ;; esac; ok $? "every harness file at its sha256: $r"
r=$(sha256sum -c $E/SHA256SUMS-e202-registration 2>&1 | grep -c ': OK$'); [ "$r" = 12 ]; ok $? "the registration's list: $r of 12 OK"
r=$(/usr/bin/python3 -I -B $E/forecast_e202.py --check | tail -c 300); case "$r" in *'"check": "PASS"'*) true ;; *) false ;; esac; ok $? "the registration's forecast re-made: $(echo "$r" | cut -c1-120)"
r=$(/usr/bin/python3 -I -B $E/plan_e202.py --check); case "$r" in *'"check": "PASS"'*) true ;; *) false ;; esac; ok $? "the registration's plan re-made: $r"
cp $E/selftest-stub-e202.json "$S/stub-before.json"
r=$(/usr/bin/python3 -I -B $E/score_e202.py --selftest "$S/selftest" | cut -c1-40); cmp -s "$S/stub-before.json" $E/selftest-stub-e202.json
c=$?; case "$r" in '{"selftest": "PASS"'*) [ "$c" = 0 ] ;; *) false ;; esac; ok $? "the scorer's stand-in self-test PASS, its stub unchanged after (cmp $c)"
r=$(bash $E/preflight_e202.sh 2>&1 | grep -m1 '^dmcmd_audit: '); case "$r" in "dmcmd_audit: GO ("*", 0 disallowed; allow-list: none)") true ;; *) false ;; esac; ok $? "the preflight: $r"
w=$(bash $E/preflight_e202.sh 2>&1 | grep -c '\[WRITE'); [ "$w" = 0 ]; ok $? "no send site classed WRITE ($w)"
r=$(/usr/bin/python3 -I -B $E/rb/check_history_e202.py names); case "$r" in "SHADOW NAMES: "*) true ;; *) false ;; esac; ok $? "the history check's shadow names: $(echo "$r" | cut -c1-160)"
r=$(/usr/bin/python3 -I -B $E/v3note_e202.py --check); case "$r" in "V3NOTE CHECK PASS"*) true ;; *) false ;; esac; ok $? "the ledger v3 note re-made (fix-e202): $(echo "$r" | cut -c1-200)"
bad=""; for f in $(find $E -name '*.sh' | LC_ALL=C sort); do bash -n "$f" 2> /dev/null || bad="$bad $f"; done
[ -z "$bad" ]; ok $? "bash -n on every shell file of the kit:${bad:- all parse}"
r=$(/usr/bin/python3 -I -B - $E <<'PY'
import ast, os, sys
bad = []
n = 0
for dp, dn, fn in os.walk(sys.argv[1]):
    for f in fn:
        if f.endswith(".py"):
            n += 1
            try:
                ast.parse(open(os.path.join(dp, f)).read())
            except SyntaxError as e:
                bad.append(f"{f}: {e}")
print(f"{n} Python files parsed, {len(bad)} with a syntax error" + (": " + "; ".join(bad) if bad else ""))
sys.exit(1 if bad else 0)
PY
); c=$?; ok $c "$r"
w=$(grep -nE "open\([^)]*['\"]/(etc|usr|opt|var|sys|proc|dev)/|> */(etc|usr|opt|var|sys|dev)/" $E/run_e202.py $E/build_e202.sh $E/files_e202.sh $E/session_e202.sh $E/hostcheck_e202.py | grep -v '/dev/null\|/dev/stdout' | grep -c .)
[ "$w" = 0 ]; ok $? "the box-side files write nothing under a system path ($w lines)"
echo "CHECKS-E202 $n of $m $([ "$n" = "$m" ] && echo PASS || echo FAIL)"
[ "$n" = "$m" ]
