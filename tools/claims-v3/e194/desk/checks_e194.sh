#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration and before any E194 datum): the kit's quick set, from the top of the tree,
# under /usr/bin/python3 (named in the output): E191's quick set (tools/claims-v3/e191/desk/checks_e191.sh, unchanged beside it) on E194's
# files: every Python file compiles and every shell file parses; both modules' self-checks; the README checker's self-test, and the checker on
# E189's committed README (it names the missing host.rec); the harness re-made and at its sha256; PLANS SAME; E189's host check's frozen
# lines; the registration's plan and forecast re-made and the scorer's E59 self-test; the history check's names; the never-run check
# (E189's and both of E191's data folders left out: fix-e194) and that step 2 leaves out the same folders; the runbook's command lines (desk/drylisting_check_e194.py on logs/dry-listing-e194.txt); the collector's
# tree name equal to the common module's; the parser's and the identity test's committed logs. A desk check of code: nothing is measured.
#   bash tools/claims-v3/e194/desk/checks_e194.sh > tools/claims-v3/e194/logs/checks-e194.txt    (the last line: CHECKS-E194 <n> of <m> PASS)
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." || exit 2
E=tools/claims-v3/e194
PY=/usr/bin/python3
n=0; m=0
c() {  # c <name> <want: a grep -E pattern on the output> <command...>
  local name=$1 want=$2; shift 2
  local out; out=$("$@" 2>&1); local rc=$?
  m=$((m + 1))
  if printf '%s\n' "$out" | grep -qE -- "$want"; then n=$((n + 1)); echo "PASS $name: $(printf '%s\n' "$out" | grep -E -- "$want" | tail -n 1 | cut -c1-200)"
  else echo "FAIL $name (rc $rc): $(printf '%s\n' "$out" | tail -n 3 | tr '\n' ' ' | cut -c1-300)"; fi
}
echo "checks_e194: $(date '+%F %T %Z') on $(hostname), $($PY --version 2>&1) at $PY, $(bash --version | head -n 1)"
bad=$($PY -I -B - $(find $E -name '*.py' | LC_ALL=C sort) <<'PY'
import sys
bad = []
for f in sys.argv[1:]:
    try:
        compile(open(f).read(), f, "exec")       # in memory: no __pycache__ is written into the kit's folder
    except SyntaxError as e:
        bad.append(f"{f} ({e})")
print(" ".join(bad))
PY
)
m=$((m + 1)); [ -z "$bad" ] && { n=$((n + 1)); echo "PASS python: every .py under $E compiles (in memory)"; } || echo "FAIL python: $bad"
bad=""; for f in $(find $E -name '*.sh' | LC_ALL=C sort); do bash -n "$f" 2> /dev/null || bad="$bad $f"; done
m=$((m + 1)); [ -z "$bad" ] && { n=$((n + 1)); echo "PASS shell: every .sh under $E parses (bash -n)"; } || echo "FAIL shell:$bad"
c common '^E194-COMMON SELF-CHECK PASS' $PY -I -B $E/e194_common.py
c ident '^E194-IDENT SELF-CHECK PASS' $PY -I -B $E/e194_ident.py
c readme-selftest '^README-CHECK-E194 SELFTEST PASS' $PY -I -B $E/rb/readme_check_e194.py --selftest
D189=docs/reports/data/2026-11-14-e189-blind-day-aifoundry3
c readme-on-e189 "the Files table does not name: .*host\.rec" $PY -I -B - "$D189" <<'PY'
import os, sys
sys.path.insert(0, "tools/claims-v3/e194/rb")
import readme_check_e194 as R
d = sys.argv[1]
files = [ln.split("  ", 1)[1].strip() for ln in open(os.path.join(d, "SHA256SUMS")) if "  " in ln]
why = R.check(open(os.path.join(d, "README.md")).read().replace("# E189", "# E194", 1), files)
print("E189's committed README read by E194's checker (its title read as E194's; its SHA256SUMS as FILES.txt): " + "; ".join(w for w in why if "Files table" in w))
PY
c harness-check '^CHECK PASS' $PY -I -B $E/check_e194.py --check
c harness-box '^HARNESS OK: [0-9]+ files' $PY -I -B $E/check_e194.py --box
c plans '^PLANS SAME' $PY -I -B $E/check_e194.py --plans
c hostcheck-json '^HOSTCHECK-JSON CHECK PASS' $PY -I -B tools/claims-v3/e189/hostcheck_e189.py --check-json
c plan '^PLAN CHECK PASS' $PY -I -B $E/plan_e194.py --check
c forecast '^FORECAST CHECK PASS' $PY -I -B $E/forecast_e194.py --check
c selftest-e59 '"verdict": "PASS"' $PY -I -B $E/score_e194.py --selftest-e59
c history-names '^SHADOW NAMES: ' $PY -I -B $E/rb/check_history_e194.py names
c never-ran '^NEVER RAN' $PY -I -B workloads/ledger/spp_never_ran.py --exclude docs/reports/data/2026-11-12-q166-progs \
  --exclude docs/reports/data/2026-11-14-e189-blind-day-aifoundry3 --exclude docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1 \
  --exclude docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2 --n 544 --k 4 --eta 0.39 --m 1792 --seed 3
# fix-e194 (verify-e194's finding 1): step 2's never-run command and this one leave out the same folders, both of E191's among them
c never-ran-same '^NEVER-RAN EXCLUDES SAME' $PY -I -B - <<'PY'
import re
def ex(p):
    lines = open(p).read().split("\n")
    i = next(n for n, ln in enumerate(lines) if "-I -B workloads/ledger/spp_never_ran.py" in ln)
    cmd = [lines[i]]
    while cmd[-1].rstrip().endswith("\\"):
        i += 1
        cmd.append(lines[i])
    return sorted(re.findall(r"--exclude (\S+)", " ".join(cmd)))
a, b = ex("tools/claims-v3/e194/rb/s03_desk_e194.sh"), ex("tools/claims-v3/e194/desk/checks_e194.sh")
want = {"docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1", "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2"}
print(("NEVER-RAN EXCLUDES SAME: " if a == b and want <= set(a) else "NEVER-RAN EXCLUDES DIFFER: ") + ", ".join(a) + (" | " + ", ".join(b) if a != b else ""))
PY
c runbook-lines '^DRYLISTING-CHECK-E194 PASS' $PY -I -B $E/desk/drylisting_check_e194.py $E/logs/dry-listing-e194.txt
c etdevices-reading-no '^no: ' bash $E/etdevices_e194.sh /dev/null /dev/null
c tree-name '^TREE SAME' $PY -I -B -c "import sys; sys.path.insert(0, '$E'); import e194_common as C, collect_e194 as K; print('TREE SAME' if C.TREE == K.TREE == 'claude/et-soc1-prototyping' else 'TREE DIFFERS')"
c parser-log '^PARSER-E194 [0-9]+ of [0-9]+ PASS' cat $E/logs/parser-e194.txt
c identity-log '^IDENTITY-E194 [0-9]+ of [0-9]+ PASS' cat $E/logs/identity-e194.txt
echo "CHECKS-E194 $n of $m $([ "$n" -eq "$m" ] && echo PASS || echo FAIL)"
[ "$n" -eq "$m" ]
