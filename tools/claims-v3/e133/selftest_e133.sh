#!/bin/bash
# E133 (Q136): the scorer's self-test and the preflight, from the top of the lab clone; writes tools/claims-v3/e133/selftest.txt.
#   bash tools/claims-v3/e133/selftest_e133.sh <scratch dir> [<dry-run data dir>]
# 1. the regression: E98's and E111's committed results.json reproduced by the scorer's own code path, key for key;
# 2. the scorer on E111's committed data posed as E133's (symlinks in <scratch dir>): every rule scored, R1 at ratio 1.000;
# 3. the dry run (the whole queue with --dry, the toy card, no device): its steps and exits, and the scorer on it;
# 4. the device-command audit (dmcmd_audit.py) over the chain, with the one reviewed exception.
set -u
S=${1:?scratch dir}; DRY=${2:-}
OUT=tools/claims-v3/e133/selftest.txt
E111=docs/reports/data/2026-11-01-e111-heat-steady
EXC='tools/claims-v3/hpl/run_hpl.py:622:SP_ERROR_LOG=never sent in E133: run_e133.py wraps run_hpl.run_out so that any residency command returns at once, unsent (no process, no device opened); it logs the skip to e133-not-sent.jsonl'
{
echo "E133 self-test, $(date '+%F %T %Z'), at $(git rev-parse --short HEAD) plus the uncommitted E133 files"
echo; echo "== 1. regression =="
python3 tools/claims-v3/e133/reduce_e133.py --regression 2>&1 | tail -2
echo; echo "== 2. the scorer on E111's committed data posed as E133's (SMOKE, W2, END, W1B, END2, history, queue, phone linked) =="
P="$S/selftest-e111-as-e133"; mkdir -p "$P"
for x in SMOKE W2 END W1B END2 history queue.jsonl phone.jsonl; do ln -sfn "$PWD/$E111/$x" "$P/$x"; done
python3 tools/claims-v3/e133/reduce_e133.py "$P" --out "$S/selftest-e111-as-e133-results.json" > "$S/selftest-e111-as-e133-reduce.txt" 2>&1
echo "rc=$?"; sed -n '/^VERDICTS/,/tally/p' "$S/selftest-e111-as-e133-reduce.txt"
grep -E '^  (R1|R2|A3) ' "$S/selftest-e111-as-e133-reduce.txt" | cut -c1-400
grep -E 'B3c:' "$S/selftest-e111-as-e133-reduce.txt" | cut -c1-600
if [ -n "$DRY" ]; then
  echo; echo "== 3. the dry run on the Intel ($(basename "$DRY"), the toy card; no device, no lock): the queue's steps =="
  grep -h '"kind": "\(start\|end\|skip\|queue_end\)"' "$DRY/queue.out" | python3 -c 'import json,sys
for ln in sys.stdin:
    d = json.loads(ln[ln.index("{"):])
    print(" ", ln[:12], d["kind"], d.get("step", ""), "rc", d.get("rc"), "cap", (d.get("cmd") or [None] * 7)[6] if d["kind"] == "start" else "", d.get("why", ""), d.get("step_card_min", ""))'
  echo "  residency commands answered unsent in the dry run: $(cat "$DRY"/runs/*/e133-not-sent.jsonl 2>/dev/null | wc -l | tr -d ' ') (a dry session sends no query at all)"
fi
echo; echo "== 3b. the budget rule and the session cap, dry: budget 3 card-min, steps SMOKE,END2 (SMOKE's cap cut to 2.5; END2 refused) =="
B3="$S/dry-budget-$(date +%H%M%S)"; mkdir -p "$B3/runs"   # a fresh directory: a session never reuses a run directory
now=$(date +%H:%M); late=$(date -v+20M +%H:%M 2>/dev/null || date -d '+20 min' +%H:%M); cut=$(date -v+30M +%H:%M 2>/dev/null || date -d '+30 min' +%H:%M)
python3 tools/claims-v3/e133/make_schedule_e133.py --date "$(date +%F)" --smoke-not-before "$now" --smoke-latest "$late" --w3-not-before "$now" \
  --w3-latest "$late" --no-start-after "$late" --cutoff "$cut" --budget 3 --out "$B3/schedule.json" > /dev/null
timeout 600 python3 tools/claims-v3/e133/queue_e133.py --schedule "$B3/schedule.json" --runs "$B3/runs" --steps SMOKE,END2 --dry > "$B3/queue.out" 2>&1 < /dev/null
echo "  rc=$?"
grep -h '"kind": "\(start\|end\|skip\|queue_end\)"' "$B3/queue.out" | python3 -c 'import json,sys
for ln in sys.stdin:
    d = json.loads(ln[ln.index("{"):])
    print("   ", d["kind"], d.get("step", ""), "rc", d.get("rc"), "cap", (d.get("cmd") or [None] * 7)[6] if d["kind"] == "start" else "", d.get("why", ""))'

echo; echo "== 4. the device-command audit (Q136(w)'s checker and table as committed at $(git log -1 --format=%h -- tools/claims-v3/dmcmd_audit.py)) =="
A="$S/audit-head"; mkdir -p "$A"
git show "$(git log -1 --format=%H -- tools/claims-v3/dmcmd_audit.py)":tools/claims-v3/dmcmd_audit.py > "$A/dmcmd_audit.py"
git show "$(git log -1 --format=%H -- tools/claims-v3/dmcmd_table.json)":tools/claims-v3/dmcmd_table.json > "$A/dmcmd_table.json"
LT=$(grep -n '^r1 = Mod.run_out' tools/claims-v3/e133/selftest_e133.sh | head -1 | cut -d: -f1)
EXT="tools/claims-v3/e133/selftest_e133.sh:$LT:SP_ERROR_LOG=the unit check of section 5: a stand-in run_out records the argv; nothing is executed and no device is opened"
CHAIN="tools/claims-v3/e133/ tools/claims-v3/e111/idle_logins_e111.py tools/claims-v3/kspeed/run_kspeed.py tools/claims-v3/hpl/run_hpl.py"
python3 -I "$A/dmcmd_audit.py" --table "$A/dmcmd_table.json" --except "$EXC" --except "$EXT" $CHAIN 2>&1 | sed -n '/^summary:/,$p'
python3 -I "$A/dmcmd_audit.py" --table "$A/dmcmd_table.json" --except "$EXC" --except "$EXT" $CHAIN 2>&1 | grep -E 'EXCEPTED' | sed 's/^/  /' | cut -c1-260
python3 -I "$A/dmcmd_audit.py" --table "$A/dmcmd_table.json" $CHAIN 2>&1 | grep -E '^NO-GO|^dmcmd_audit' | sed 's/^/  without the exceptions: /'
python3 -I "$A/dmcmd_audit.py" --table "$A/dmcmd_table.json" --markdown --except "$EXC" --except "$EXT" $CHAIN > "$S/dmcmd_audit.md" 2>&1
echo; echo "== 5. the residency patch, unit-checked =="
python3 - <<'PY'
import os, sys
sys.path.insert(0, "tools/claims-v3/e133")
import run_e133 as M
calls = []
class Mod:
    @staticmethod
    def run_out(cmd, *a, **kw):
        calls.append(list(cmd)); return 0, b"{}\n", b""
M.patch_no_residency(Mod)
r1 = Mod.run_out(["timeout", "10", "build/ettelem-hpl/ettelem", "residency", "2", "3", "4", "5", "6"], timeout=15)
r2 = Mod.run_out(["timeout", "10", "build/ettelem-hpl/ettelem", "config"], timeout=15)
r3 = Mod.run_out(["timeout", "10", "build/ettelem-hpl/ettelem", "sptrace", "/x/residency.bin"], timeout=15)
print("  residency ->", r1, "| passed through:", calls)
assert r1 == (None, b"", b"E133: not sent") and calls == [["timeout", "10", "build/ettelem-hpl/ettelem", "config"], ["timeout", "10", "build/ettelem-hpl/ettelem", "sptrace", "/x/residency.bin"]]
print("  OK: the residency command is answered unsent; config and sptrace (even with 'residency' inside a path) go through unchanged")
PY
} > "$OUT" 2>&1
echo "wrote $OUT"; tail -5 "$OUT"
