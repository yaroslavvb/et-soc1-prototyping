#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE QUICK SET. Every .py of the kit compiles (ast, nothing written),
# every .sh parses (bash -n); the identity module's self-check (card 1's forms pass; card 0's refused); the gate's watch reader on card 1's
# and card 0's blocks; the history check's module names; no __pycache__ under the kit; the registration's list every entry OK; E192's
# registration and kit lists every entry OK; the shared list every entry OK; the sync list's paths all present; step 2 carries the sealed
# card-1 note's path; the wait's patterns are the real script's names.
#   bash tools/claims-v3/e199/desk/checks_e199.sh <scratch dir>        (from the repository's top; prints CHECKS-E199 <n> of <m> PASS)
# SPDX-License-Identifier: Apache-2.0
set -u
S=${1:?a scratch directory}; mkdir -p "$S"
E=tools/claims-v3/e199
npass=0; ncase=0; fail=0
ok() { ncase=$((ncase + 1)); if [ "$1" = 1 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fail=1; fi; }
echo "E199 quick set (kit-e199), $(TZ=America/Los_Angeles date '+%F %T %Z'); /usr/bin/python3 $(/usr/bin/python3 -V 2>&1 | cut -d' ' -f2); bash ${BASH_VERSION}"
bad=""; n=0
while IFS= read -r f; do n=$((n + 1)); /usr/bin/python3 -I -B -c 'import ast, sys; ast.parse(open(sys.argv[1]).read(), sys.argv[1])' "$f" 2> /dev/null || bad="$bad $f"; done < <(find $E -name '*.py' | LC_ALL=C sort)
ok "$([ -z "$bad" ] && echo 1)" "C1 every .py of the kit compiles ($n files)${bad:+: $bad}"
bad=""; n=0
while IFS= read -r f; do n=$((n + 1)); bash -n "$f" 2> /dev/null || bad="$bad $f"; done < <(find $E -name '*.sh' | LC_ALL=C sort)
ok "$([ -z "$bad" ] && echo 1)" "C2 every .sh of the kit parses ($n files)${bad:+: $bad}"
o=$(/usr/bin/python3 -I -B $E/ident_e199.py selfcheck 2>&1); echo "   $o" | cut -c1-200
ok "$(echo "$o" | grep -q '^IDENT-E199 SELF-CHECK PASS' && echo 1)" "C3 the identity module's self-check"
o=$(/usr/bin/python3 -I -B tools/claims-v3/e191/e191_ident.py 2>&1 | tail -n 1)
ok "$(echo "$o" | grep -q 'E191-IDENT SELF-CHECK PASS' && echo 1)" "C4 E191's identity module's own self-check (imported unchanged)"
o=$(/usr/bin/python3 -I -B - <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("g", "tools/claims-v3/e199/gate_e199.py"); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
import e191_ident as I
b1, w1 = g.stderr_wrong(I.BLOCK.format(c=1, k="ops") * 3)
b0, w0 = g.stderr_wrong(I.BLOCK.format(c=1, k="ops") + I.BLOCK.format(c=0, k="ops"))
print("OK" if (b1 == ["1"] * 3 and not w1 and b0 == ["1", "0"] and w0 == ["/dev/et0_ops", "Physical device ID 0"]) else "BAD %s %s %s %s" % (b1, w1, b0, w0))
PY
)
ok "$([ "$o" = OK ] && echo 1)" "C5 the gate's watch reader: three card-1 blocks pass; a card-0 block among them is named ($o)"
o=$(/usr/bin/python3 -I -B $E/rb/check_history_e199.py names 2>&1 | tail -n 1)
ok "$(echo "$o" | grep -qiE 'ok|names' && echo 1)" "C6 the history check's module names read ($(echo "$o" | cut -c1-80))"
ok "$([ -z "$(find $E -name __pycache__ -o -name '*.pyc')" ] && echo 1)" "C7 no __pycache__ or .pyc under the kit"
ok "$(sha256sum -c --quiet $E/SHA256SUMS-e199-registration > /dev/null 2>&1 && echo 1)" "C8 E199's registration list: every entry OK"
ok "$(sha256sum -c --quiet tools/claims-v3/e192/SHA256SUMS-e192-registration > /dev/null 2>&1 && sha256sum -c --quiet tools/claims-v3/e192/SHA256SUMS-e192-kit > /dev/null 2>&1 && echo 1)" "C9 E192's registration and kit lists: every entry OK"
ok "$(sha256sum -c --quiet $E/SHA256SUMS-e199-shared > /dev/null 2>&1 && [ "$(grep -c . $E/SHA256SUMS-e199-shared)" = 6 ] && echo 1)" "C10 the shared list: 6 entries, every one OK"
m=0; while IFS= read -r p; do case "$p" in ''|'#'*) continue ;; esac; [ -e "$p" ] || { [ "$p" = "$E/SHA256SUMS-e199-kit" ] || m=$((m + 1)); }; done < $E/boxfiles-e199.txt
ok "$([ "$m" = 0 ] && echo 1)" "C11 every path of the sync list is present (the kit list made last)"
ok "$(grep -q 'tools/claims-v3/sealed-card1/e199-freeze-lines.md' $E/rb/s03_desk_e199.sh && grep -q '"tools/claims-v3/sealed-card1/"' $E/rb/check_history_e199.py && echo 1)" "C12 step 2 reads the sealed card-1 note's path; the history check accepts additions there"
ok "$(grep -q 'ours_live "session_${RUN}.sh"' $E/rb/s20_wait_e199.sh && grep -q 'session_e199.sh' $E/rb/s11_a1_session_e199.sh && echo 1)" "C13 step 10's pattern is step 9's launched name (session_e199.sh)"
echo; echo "CHECKS-E199 $npass of $ncase $([ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
