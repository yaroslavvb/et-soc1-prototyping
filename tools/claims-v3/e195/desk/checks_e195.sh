#!/usr/bin/env bash
# E195's kit (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): THE QUICK SET of desk checks of code, each PASS or FAIL:
#   Q1  every .py of the kit compiles and every .sh parses (bash -n);
#   Q2  harness-e195.json re-made from the files equals the committed one (CHECK PASS) and every file of it is at its sha256 (HARNESS OK);
#   Q3  the two ports re-made from their sources by their exact replacements (desk/port_e195.py --check: PORT CHECK PASS);
#   Q4  the dry listing from the kit's runner in its own dry mode equals the registration's listing but for --no-ms on every x09mem_host
#       call (desk/drylisting_e195.py: DRYLISTING-E195 PASS), and the committed desk/dry-e195-noms-aifoundry3.txt is that listing;
#   Q5  the audit table re-made from the files' own lines equals the committed desk/dry-branches-e195.tsv (DRYBRANCHES-E195 OK);
#   Q6  the device-command preflight (preflight_e195.sh): dmcmd_audit GO;
#   Q7  THE KIT'S GENERATOR OUTPUT: the registered source built here (a scratch copy; cmake with /opt/et, -j4), check_elf.py CHECK OK, the
#       host's --list --json byte for byte the registration's desk/arm-table-e195.json, and make_x09.py --check --no-ms from this host's
#       bytes byte for byte the kit's gen-e195-noms/ (manifest.json and counts.json), its counts.json the registration's desk/gen-e195/'s;
#   Q8  rest_rule_e195.sh's code is E193's rest rule line for line but its refusal line and its no-device line (Q191, lane fix-e195:
#       verify-e195's finding 4, the session's own two forms at a line's start);
#   Q9  lib_e195.sh's stop_sampler is lib.sh's but for its SIGKILL branch (the lines that differ are only that branch's);
#   Q10 the history check's names (the standard library's, the day's own) and no E195 datum in any ref (check_history_e195.py names,
#       nodatum);
#   Q11 the runbook's audit table re-made from the files' own lines equals the committed rb/dry-branches-rb-e195.tsv
#       (DRYBRANCHES-RB-E195 OK; Q191, lane fix-e195, verify-e195's nit 7; the runbook desk test checks its cases).
# Run in the round's CPU slot inside the no-device sandbox (the host runs only with --list and --dump-image):
#   bash slot.sh bash nodev.sh bash tools/claims-v3/e195/desk/checks_e195.sh <empty scratch dir> > logs/checks-e195.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
E=$(cd "$D/.." && pwd -P)
REPO=$(cd "$E/../../.." && pwd -P)
S=${1:?an empty scratch directory}
mkdir -p "$S" && S=$(cd "$S" && pwd -P); [ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
for d in /dev/et*; do [ -e "$d" ] || continue; if [ -c "$d" ]; then echo "REFUSED: $d is a device node: run inside nodev.sh"; exit 2; fi; done
PY=/usr/bin/python3
n=0; p=0
ok() { n=$((n + 1)); if [ "$1" = 1 ]; then p=$((p + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fi; }
cd "$REPO" || exit 2
echo "E195 kit quick checks, $(date '+%F %T %Z'); $($PY -V 2>&1) ($PY); bash $BASH_VERSION; $(cmake --version | head -n 1)"
bad=""
for f in $(find tools/claims-v3/e195 -name '*.py' ! -path '*/proposal/*' | LC_ALL=C sort); do $PY -I -B -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' "$f" || bad="$bad $f"; done
for f in $(find tools/claims-v3/e195 -name '*.sh' ! -path '*/proposal/*' | LC_ALL=C sort); do bash -n "$f" || bad="$bad $f"; done
ok "$([ -z "$bad" ] && echo 1)" "Q1 every kit .py compiles and every .sh parses ($(find tools/claims-v3/e195 \( -name '*.py' -o -name '*.sh' \) ! -path '*/proposal/*' | wc -l) files)${bad:+: $bad}"
a=$($PY -I -B tools/claims-v3/e195/harness_e195.py --check); b=$($PY -I -B tools/claims-v3/e195/harness_e195.py --box)
ok "$(echo "$a" | grep -q '^CHECK PASS' && echo "$b" | grep -q '^HARNESS OK' && echo 1)" "Q2 $a; $b"
a=$($PY -I -B tools/claims-v3/e195/desk/port_e195.py --check | tail -n 1)
ok "$(echo "$a" | grep -q '^PORT CHECK PASS' && echo 1)" "Q3 $a"
a=$($PY -I -B tools/claims-v3/e195/desk/drylisting_e195.py "$S/drylisting" | tail -n 1)
mkdir -p "$S/dl2"; cp tools/claims-v3/e195/desk/dry-e195-noms-aifoundry3.txt "$S/dl2/committed.txt"
c=$($PY -I -B - "$S/drylisting" "$S/dl2/committed.txt" <<'PY'
import subprocess, sys, os, re
# re-run the generator's own listing into a temporary file and compare it with the committed one, line for line
E = os.path.join(os.getcwd(), "tools/claims-v3/e195")
sys.path.insert(0, os.path.join(E, "desk"))
import drylisting_e195 as d
got = []
for p, items in [d.SMOKE] + d.PASSES:
    got += d.run(sys.argv[1] + "-2", p, items)
com = [l.rstrip("\n") for l in open(sys.argv[2]) if l.startswith("DRY hold10: ")]
print("SAME" if got == com else "DIFFERENT", len(got), len(com))
PY
)
ok "$(echo "$a" | grep -q '^DRYLISTING-E195 PASS' && echo "$c" | grep -q '^SAME' && echo 1)" "Q4 ${a:0:160}; the committed dry-e195-noms-aifoundry3.txt: $c"
$PY -I -B tools/claims-v3/e195/desk/drybranches_e195.py > "$S/db.txt"; a=$(tail -n 1 "$S/db.txt")
grep -v '^DRYBRANCHES' "$S/db.txt" > "$S/db-rows.txt"; grep -v '^#' tools/claims-v3/e195/desk/dry-branches-e195.tsv > "$S/db-com.txt"
ok "$(echo "$a" | grep -q '^DRYBRANCHES-E195 OK' && cmp -s "$S/db-rows.txt" "$S/db-com.txt" && echo 1)" "Q5 $a; the committed table equal to it: $(cmp -s "$S/db-rows.txt" "$S/db-com.txt" && echo yes || echo NO)"
a=$(bash tools/claims-v3/e195/preflight_e195.sh 2>&1 | grep -m1 "^dmcmd_audit:")
ok "$(echo "$a" | grep -q '^dmcmd_audit: GO' && echo 1)" "Q6 $a"
cp -a tools/claims-v3/e195/proposal/src "$S/src"
export LD_LIBRARY_PATH=/opt/et/lib
cmake -S "$S/src" -B "$S/build" -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > "$S/configure.log" 2>&1 && nice -n 10 cmake --build "$S/build" -j4 > "$S/build.log" 2>&1; brc=$?
H=$S/build/host/x09mem_host
ce=$($PY -I -B tools/claims-v3/e195/proposal/src/check_elf.py "$S/build/kernel/x09mem.elf" 2>&1 | tail -n 1)
"$H" --list --json > "$S/arm.json" 2>/dev/null
$PY -I -B tools/claims-v3/e195/proposal/src/make_x09.py "$S/gen" --host "$H" --check --no-ms > "$S/make.txt" 2>&1; mrc=$?
g1=$(cmp -s "$S/gen/manifest.json" tools/claims-v3/e195/gen-e195-noms/manifest.json && cmp -s "$S/gen/counts.json" tools/claims-v3/e195/gen-e195-noms/counts.json && echo yes || echo NO)
g2=$(cmp -s "$S/gen/counts.json" tools/claims-v3/e195/desk/gen-e195/counts.json && echo yes || echo NO)
al=$(cmp -s "$S/arm.json" tools/claims-v3/e195/desk/arm-table-e195.json && echo yes || echo NO)
kt=$(/opt/et/bin/riscv64-unknown-elf-objcopy -O binary --only-section=.text "$S/build/kernel/x09mem.elf" /dev/stdout | sha256sum | cut -c1-16)
ok "$([ "$brc" = 0 ] && echo "$ce" | grep -q '^CHECK OK' && [ "$mrc" = 0 ] && [ "$g1" = yes ] && [ "$g2" = yes ] && [ "$al" = yes ] && echo 1)" \
  "Q7 the build rc $brc; $ce; .text ${kt}... (the registration's desk build 007a355d2da5b420...); the arm table byte-equal: $al; $(tail -n 1 "$S/make.txt"); gen-e195-noms/ byte-equal: $g1; counts.json equal to the registration's desk/gen-e195/: $g2"
c=$($PY -I -B - <<'PY'
a = open("tools/claims-v3/e193/rb/rest_rule_e193.sh").read(); b = open("tools/claims-v3/e195/rb/rest_rule_e195.sh").read()
a = a[a.index("latest_write() {"):].splitlines(); b = b[b.index("latest_write() {"):].splitlines()
d = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
nd = "inblk && (m ~ /^refused, no device opened: / || (m ~ /^GATE-STOP: / && m ~ /\\(no device opened\\)$/)) { nodev = 1 }"
print(len(a), len(b), d, len(d) == 2 and a[d[0]].strip() == "inblk && /no device opened/ { nodev = 1 }" and b[d[0]].strip() == nd
      and "E195's first card command" in b[d[1]])
PY
)
ok "$(echo "$c" | grep -q '^60 60 \[22, 55\] True$' && echo 1)" "Q8 the rest rule's code lines (E193's, E195's, the lines that differ: the no-device line and the refusal's words): $c"
c=$($PY -I -B - <<'PY'
import re
def fn(path, name):
    t = open(path).read(); i = t.index(name + "() {"); j = t.index("\n}\n", i); return t[i:j + 2].splitlines()
a = fn("tools/claims-v3/lib.sh", "stop_sampler"); b = fn("tools/claims-v3/e195/lib_e195.sh", "stop_sampler")
import difflib
d = [l for l in difflib.unified_diff(a, b, lineterm="", n=0) if l[:1] in "+-" and not l.startswith(("+++", "---"))]
removed = [l for l in d if l.startswith("-")]; added = [l for l in d if l.startswith("+")]
print(len(removed), len(added), all(("SIGKILL" in l or "kill -KILL" in l or l.strip() in ("-    # 30 s after SIGTERM it is stuck inside a request: the queue is already blocked, so kill it and drain the reply",)) for l in removed))
PY
)
ok "$(echo "$c" | grep -q ' True$' && echo 1)" "Q9 lib_e195.sh's stop_sampler against lib.sh's (lines removed, added, every removed line the SIGKILL branch's): $c"
a=$($PY -I -B tools/claims-v3/e195/rb/check_history_e195.py names | cut -c1-140); b=$($PY -I -B tools/claims-v3/e195/rb/check_history_e195.py nodatum)
ok "$(echo "$b" | grep -q '^NO-DATUM OK' && echo "$a" | grep -q '^SHADOW NAMES' && echo 1)" "Q10 $a; $b"
$PY -I -B tools/claims-v3/e195/rb/drybranches_rb_e195.py > "$S/dbrb.txt"; a=$(tail -n 1 "$S/dbrb.txt")
grep -v '^DRYBRANCHES' "$S/dbrb.txt" > "$S/dbrb-rows.txt"; grep -v '^#' tools/claims-v3/e195/rb/dry-branches-rb-e195.tsv > "$S/dbrb-com.txt"
ok "$(echo "$a" | grep -q '^DRYBRANCHES-RB-E195 OK' && cmp -s "$S/dbrb-rows.txt" "$S/dbrb-com.txt" && echo 1)" "Q11 $a; the committed table equal to it: $(cmp -s "$S/dbrb-rows.txt" "$S/dbrb-com.txt" && echo yes || echo NO)"
echo; echo "CHECKS-E195 $p of $n $([ "$p" = "$n" ] && echo PASS || echo FAIL)"
[ "$p" = "$n" ]
