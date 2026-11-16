#!/usr/bin/env bash
# E191's kit, dated note 3 (Q190, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after E191's
# second session's data commit 7156ac15 of Sun 15 Nov 2026, 14:32:17 PST): THE QUICK SET v3, from the top of the tree under /usr/bin/python3
# (named in the output), in desk/checks_e191_v2.sh's form (unchanged beside it): every .py under the kit compiles and every .sh parses; step 9
# v3 and step 11 v3 are their v2 files with the stated exact replacements (desk/v3from_v2_e191.py --check); every list step 2 v3 pins but
# note 3's and A2's (which pin this check's own log) is at its pinned count and own sha256 with every entry OK (step 2 v3 reads all sixteen;
# the go's anchor lines give step 2 v3's own sha256); the names the new steps share agree (the second session's
# record, the third's directory form, the registered verdicts' bytes); the second session's record reads every entry OK in both its lists;
# THE REGISTERED VERDICTS RE-DERIVED: the frozen scorer on that committed record writes 23484c4f... byte for byte (its four words FAIL, PASS,
# FAIL, FAIL); repeat_e191.py's self-test on that output; the preflight v2 GO (no new device-command site: the third session runs session v2
# and runner v2 unchanged); the runbook's command lines (desk/drylisting_check_e191_v2.py on logs/dry-listing-e191-v3.txt); the history
# check's names and no new file shadowing a module; and THE NEVER-RUN CHECK (a) in A2's form at this tree (E191's two earlier records and
# E194's committed folders of their exact form left out). A desk check of code: nothing is measured.
#   bash tools/claims-v3/e191/desk/checks_e191_v3.sh > tools/claims-v3/e191/logs/checks-e191-v3.txt    (last line: CHECKS-E191-V3 <n> of <m> PASS)
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." || exit 2
E=tools/claims-v3/e191
PY=/usr/bin/python3
SECOND=docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2
FIRST=docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1
S2SHA=23484c4f546595a728f0c7ffe59e9414d125473108f06891e5dd53283d62ecb8
TMPD=$(mktemp -d "${TMPDIR:-/tmp}/checks-e191-v3.XXXXXX") || exit 2
n=0; m=0
c() {  # c <name> <want: a grep -E pattern on the output> <command...>
  local name=$1 want=$2; shift 2
  local out; out=$("$@" 2>&1); local rc=$?
  m=$((m + 1))
  if printf '%s\n' "$out" | grep -qE -- "$want"; then n=$((n + 1)); echo "PASS $name: $(printf '%s\n' "$out" | grep -E -- "$want" | tail -n 1 | cut -c1-240)"
  else echo "FAIL $name (rc $rc): $(printf '%s\n' "$out" | tail -n 3 | tr '\n' ' ' | cut -c1-300)"; fi
}
echo "checks_e191_v3: $(date '+%F %T %Z') on $(hostname), $($PY --version 2>&1) at $PY, $(bash --version | head -n 1)"
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
c v3-from-v2 '^V3-FROM-V2 SAME' $PY -I -B $E/desk/v3from_v2_e191.py --check
c step2-v3-pins '^STEP2-V3 PINS OK' $PY -I -B - "$E/rb/s03_desk_e191_v3.sh" <<'PY'
import hashlib, os, re, sys
src = open(sys.argv[1]).read()
allspecs = re.findall(r"([A-Za-z0-9_./-]*SHA256SUMS[A-Za-z0-9_.-]*):([0-9]+):([0-9a-f]{64}):(top|beside)", src)
own = ("SHA256SUMS-e191-kit-note3", "SHA256SUMS-e191-a2")      # note 3's and A2's lists pin this check's own log: step 2 v3 and the anchor lines read them
specs = [s for s in allspecs if not s[0].endswith(own)]
bad = []
for path, cnt, h, form in specs:
    try:
        b = open(path, "rb").read()
    except OSError as e:
        bad.append(f"{path}: {e}"); continue
    lines = [ln for ln in b.decode().splitlines() if ln.strip()]
    if len(lines) != int(cnt) or hashlib.sha256(b).hexdigest() != h:
        bad.append(f"{path} ({len(lines)} lines, sha256 {hashlib.sha256(b).hexdigest()[:12]}; pinned {cnt}, {h[:12]})")
    base = "." if form == "top" else os.path.dirname(path)
    for ln in lines:
        hh, p = ln.split(None, 1)
        q = os.path.join(base, p.lstrip("*"))
        if not os.path.isfile(q) or hashlib.sha256(open(q, "rb").read()).hexdigest() != hh:
            bad.append(f"{path}: {p} not at its sha256"); break
print(("STEP2-V3 PINS OK" if not bad and len(specs) == 14 and len(allspecs) == 16 else "STEP2-V3 PINS BAD: " + "; ".join(bad[:6])) +
      f": {len(specs)} of the {len(allspecs)} lists step 2 v3 pins, each at its count and own sha256 with every entry at its sha256 (note 3's "
      f"and A2's lists, which pin this check's log, are read by step 2 v3 itself and by the go's anchor lines)")
PY
c names-same '^NAMES SAME' $PY -I -B - "$E" <<'PY'
import re, sys
E = sys.argv[1]
r = lambda p: open(f"{E}/{p}").read()
s2, s9, s11, s13, t3 = r("rb/s03_desk_e191_v3.sh"), r("rb/s11_a1_session_e191_v3.sh"), r("rb/s22_collect_e191_v3.sh"), r("rb/s24_score_e191_v3.sh"), r("rb/selftest_rb_e191_v3.sh")
sec = "SECOND=docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2"
d3 = "DATA=docs/reports/data/${RB_DAY:-DAY}-e191-blind-day-aifoundry1-c1-s3"
sha = "23484c4f546595a728f0c7ffe59e9414d125473108f06891e5dd53283d62ecb8"
ok = {"the second record (steps 2 v3, 13 v3, the test)": sec in s2 and sec in s13 and sec in t3,
      "the third directory (steps 11 v3, 13 v3)": d3 in s11 and d3 in s13,
      "the registered verdicts' bytes (step 13 v3, the test)": f"S2SHA={sha}" in s13 and f"S2SHA={sha}" in t3,
      "the second session's T0 (step 9 v3's last launch, step 11 v3's refusal, the test)": "E191_FIRST_T0=1794780355" in s9 and "1794766494|1794780355)" in s11 and "ST0=1794780355" in t3,
      "both earlier records left out of the never-run check (a) (step 2 v3)": '--exclude "$FIRST" --exclude "$SECOND" $EX194' in s2}
print(("NAMES SAME" if all(ok.values()) else "NAMES DIFFER: " + ", ".join(k for k, v in ok.items() if not v)) + ": " + "; ".join(ok))
PY
second_sums() {  # the second session's record: both its lists, every entry OK
  local a b
  a=$(cd "$SECOND" && shasum -a 256 -c SHA256SUMS 2>&1 | grep -c ': OK$'); b=$(cd "$SECOND" && shasum -a 256 -c SHA256SUMS-note1 2>&1 | grep -c ': OK$')
  [ "$a" = 257 ] && [ "$b" = 7 ] && echo "SECOND-RECORD OK: SHA256SUMS $a of 257, SHA256SUMS-note1 $b of 7" || echo "SECOND-RECORD BAD: $a of 257, $b of 7"
}
s2_scores() {  # the frozen scorer on the second session's committed record: its output's sha256 and its four words
  $PY -I -B $E/score_e191.py "$SECOND" --out "$TMPD/scores-e191-s2.json" > "$TMPD/s2.out" 2>&1
  printf 'S2-SCORES %s words %s\n' "$(sha256sum "$TMPD/scores-e191-s2.json" | cut -c1-64)" "$(tr -d ' \n' < "$TMPD/s2.out")"
}
c second-record-sums "^SECOND-RECORD OK" second_sums
c registered-verdicts "^S2-SCORES $S2SHA" s2_scores
c repeat-selftest '^REPEAT-E191 SELFTEST 8 of 8 PASS' $PY -I -B $E/repeat_e191.py --selftest "$TMPD/scores-e191-s2.json"
c preflight-v2 '^dmcmd_audit: GO' bash $E/preflight_e191_v2.sh
c drylisting-v3 '^DRYLISTING-CHECK-E191 PASS' $PY -I -B $E/desk/drylisting_check_e191_v2.py $E/logs/dry-listing-e191-v3.txt
c history-names '^SHADOW NAMES: ' $PY -I -B $E/rb/check_history_e191.py names
c no-shadow '^NO SHADOW' $PY -I -B - "$E" <<'PY'
import os, subprocess, sys
E = sys.argv[1]
at = set(subprocess.run(["git", "ls-tree", "-r", "--name-only", "7156ac15", "--", E], capture_output=True, text=True).stdout.split())
new = sorted(p for p in (os.path.join(dp, f) for dp, dn, fn in os.walk(E) for f in fn) if p.endswith(".py") and p not in at)
sys.path.insert(0, os.path.join(E, "rb"))
import check_history_e191 as H
names = {os.path.basename(p)[:-3] for p in new}
hit = sorted(n for n in names if n in sys.stdlib_module_names or n in H.MODULES)
print(("NO SHADOW" if not hit else "SHADOW: " + ", ".join(hit)) + f": note 3's {len(new)} new Python files ({', '.join(sorted(names))}) against "
      f"{len(sys.stdlib_module_names)} standard-library names and the history check's {len(H.MODULES)} day modules")
PY
EX194=""; for d in docs/reports/data/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-e194-blind-day-aifoundry2; do [ -d "$d" ] && EX194="$EX194 --exclude $d"; done
c never-ran-a2 '^NEVER RAN' $PY -I -B workloads/ledger/spp_never_ran.py --exclude docs/reports/data/2026-11-12-q166-progs \
  --exclude docs/reports/data/2026-11-14-e189-blind-day-aifoundry3 --exclude "$FIRST" --exclude "$SECOND" $EX194 --n 544 --k 4 --eta 0.39 --m 1792 --seed 3
echo "(the never-run check (a) left out E194's folders:${EX194:- none})"
rm -rf "${TMPD:?}"
echo "CHECKS-E191-V3 $n of $m $([ "$n" -eq "$m" ] && echo PASS || echo FAIL)"
[ "$n" -eq "$m" ]
