#!/usr/bin/env bash
# E191's kit, dated note 2 (Q184, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after
# E191's first session stopped at its smoke gate (1a4bc1e3), before any E191 pass datum): THE QUICK SET v2, from the top of the tree under
# /usr/bin/python3 (named in the output), in desk/checks_e191.sh's form (unchanged beside it): every .py under the kit compiles and every
# .sh parses; the common module v2's self-check (v1's inside it) and v1's two; harness v2 re-made and at its sha256, v1's still at its 42;
# the preflight v2 GO; runner v2 reads no stdout through v1's last_json and imports e191_common_v2; THE DOUBLES' FORM against the committed
# bytes (fake_card_e191_v2.py's ledger host, run with the day's smoke command line, prints the head in the real host's key order and the
# runtime line at the same place as 1a4bc1e3's stdout.txt, and its line reads PASS through the reader); the runbook's command lines
# (desk/drylisting_check_e191_v2.py on logs/dry-listing-e191-v2.txt); the history check's names, no new file shadowing a module,
# and the never-run check (a) with the first session's record present. A desk check of code: nothing is measured.
#   bash tools/claims-v3/e191/desk/checks_e191_v2.sh > tools/claims-v3/e191/logs/checks-e191-v2.txt    (last line: CHECKS-E191-V2 <n> of <m> PASS)
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." || exit 2
E=tools/claims-v3/e191
PY=/usr/bin/python3
n=0; m=0
c() {  # c <name> <want: a grep -E pattern on the output> <command...>
  local name=$1 want=$2; shift 2
  local out; out=$("$@" 2>&1); local rc=$?
  m=$((m + 1))
  if printf '%s\n' "$out" | grep -qE -- "$want"; then n=$((n + 1)); echo "PASS $name: $(printf '%s\n' "$out" | grep -E -- "$want" | tail -n 1 | cut -c1-220)"
  else echo "FAIL $name (rc $rc): $(printf '%s\n' "$out" | tail -n 3 | tr '\n' ' ' | cut -c1-300)"; fi
}
echo "checks_e191_v2: $(date '+%F %T %Z') on $(hostname), $($PY --version 2>&1) at $PY, $(bash --version | head -n 1)"
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
c common-v2 '^E191-COMMON-V2 SELF-CHECK PASS' $PY -I -B $E/e191_common_v2.py
c common '^E191-COMMON SELF-CHECK PASS' $PY -I -B $E/e191_common.py
c ident '^E191-IDENT SELF-CHECK PASS' $PY -I -B $E/e191_ident.py
c harness-v2-check '^CHECK PASS \(v2\)' $PY -I -B $E/check_e191_v2.py --check
c harness-v2-box '^HARNESS-V2 OK: 49 files' $PY -I -B $E/check_e191_v2.py --box
c harness-v1-box '^HARNESS OK: 42 files' $PY -I -B $E/check_e191.py --box
c harness-v1-check '^CHECK PASS$' $PY -I -B $E/check_e191.py --check
c preflight-v2 '^dmcmd_audit: GO' bash $E/preflight_e191_v2.sh
c runner-v2-reader '^RUNNER-V2 READER OK' $PY -I -B - "$E/run_e191_v2.py" <<'PY'
import re, sys
src = open(sys.argv[1]).read()
calls = [ln for ln in src.splitlines() if re.search(r"\blast_json\(", ln.split("#", 1)[0])]
imp = "import e191_common_v2 as C" in src
reads = len(re.findall(r"C\.host_result\(", src)), len(re.findall(r"C\.config_json\(", src))
print(("RUNNER-V2 READER OK" if not calls and imp and reads == (2, 1) else "RUNNER-V2 READER BAD") +
      f": last_json calls {len(calls)}; imports e191_common_v2 {imp}; host_result calls {reads[0]} (the smoke, each pass), config_json {reads[1]}")
PY
c doubles-form '^DOUBLES-FORM OK' $PY -I -B - "$E" <<'PY'
import json, os, re, subprocess, sys
E = sys.argv[1]
d = "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/session/smoke/copy-64m-random"
real = open(os.path.join(d, "stdout.txt")).read()
argv = json.load(open(os.path.join(d, "smoke.json")))["argv"]
env = {k: v for k, v in os.environ.items() if not k.startswith("E191_FAKE_")}
env.update({"E191_FAKE_SCALE": "0.02"})
r = subprocess.run(["/usr/bin/python3", "-I", "-B", os.path.join(E, "fake_card_e191_v2.py"), "host-ledger"] + argv[1:], capture_output=True,
                   text=True, env=env, timeout=60)
fake = r.stdout
keys = lambda t: re.findall(r'"([a-z_0-9]+)":', t.replace("Opening device 1\n", ""))
pos = lambda t: t.index("Opening device 1\n") if "Opening device 1\n" in t else -1
sys.path.insert(0, E)
import e191_common_v2 as C
j, rec = C.host_result(fake, "ledger", argv)
same_keys = keys(fake)[:len(keys(real))] == keys(real)
same_place = real[pos(real) - 10:pos(real)] == fake[pos(fake) - 10:pos(fake)] == '"width":32'
print(("DOUBLES-FORM OK" if same_keys and same_place and j.get("status") == "PASS" and r.returncode == 0 else "DOUBLES-FORM BAD") +
      f": the double's keys in the real host's order {same_keys} (the double adds 'fake' after them); the runtime line after the same 10 bytes "
      f"({real[pos(real) - 10:pos(real)]!r}) {same_place}; its line read {j.get('status')}, dropped {rec['runtime_lines']}")
PY
c drylisting-v2 '^DRYLISTING-CHECK-E191 PASS' $PY -I -B $E/desk/drylisting_check_e191_v2.py $E/logs/dry-listing-e191-v2.txt
c history-names '^SHADOW NAMES: ' $PY -I -B $E/rb/check_history_e191.py names
c no-shadow '^NO SHADOW' $PY -I -B - "$E" <<'PY'
import os, subprocess, sys
E = sys.argv[1]
at = set(subprocess.run(["git", "ls-tree", "-r", "--name-only", "1a4bc1e3", "--", E], capture_output=True, text=True).stdout.split())
new = sorted(p for p in (os.path.join(dp, f) for dp, dn, fn in os.walk(E) for f in fn) if p.endswith(".py") and p not in at)
sys.path.insert(0, os.path.join(E, "rb"))
import check_history_e191 as H
names = {os.path.basename(p)[:-3] for p in new}
hit = sorted(n for n in names if n in sys.stdlib_module_names or n in H.MODULES)
print(("NO SHADOW" if not hit else "SHADOW: " + ", ".join(hit)) + f": note 2's {len(new)} new Python files ({', '.join(sorted(names))}) against "
      f"{len(sys.stdlib_module_names)} standard-library names and the history check's {len(H.MODULES)} day modules")
PY
c never-ran '^NEVER RAN' $PY -I -B workloads/ledger/spp_never_ran.py --exclude docs/reports/data/2026-11-12-q166-progs \
  --exclude docs/reports/data/2026-11-14-e189-blind-day-aifoundry3 --n 544 --k 4 --eta 0.39 --m 1792 --seed 3
echo "CHECKS-E191-V2 $n of $m $([ "$n" -eq "$m" ] && echo PASS || echo FAIL)"
[ "$n" -eq "$m" ]
