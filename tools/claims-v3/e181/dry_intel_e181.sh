#!/usr/bin/env bash
# E181 (M11's session 2): DRY-INTEL, the V3_DRY dry pass on the Intel (it never opens a device and never runs ssh), in E178's form
# (tools/claims-v3/e178/dry_intel_e178.sh) but in a tree built FROM STEP 7'S SYNC LIST ALONE: tools/claims-v3/e181/ and every repo file of
# frozen-e181.sha256, nothing else. So a file the session needs and step 7 does not copy fails here (E174's defect class: the day critic's
# kit-v4 item "gate and sync must agree, tested in a tree built from the sync list alone"). The three box binaries are absent, as E181_DESK=1
# lists them (block_e181.sh and session_e181.sh). A shim directory sits first on PATH: hostname prints aifoundry3 (lib.sh takes the card's
# name from it); date runs GNU date (the scripts use date -d); python3 is the Intel's /usr/bin/python3; et-who prints a stand-in line; ssh,
# rsync and scp are stand-ins that log the call and exit 97, so any network call fails the pass. With V3_DRY=1 E181_DESK=1 (E97's toy card:
# a virtual clock, a die that always reads 51 C, a 34-sensor mean of 51.433 C, a board that never rises):
#   A  the session: the gates, the box list (27 OK, 3 box-only listed), the preflight GO, A6-1's floor mark, the smoke with its five stop
#      tests, the smoke gate (NO-GO on the toy, expected); it writes build/e181/session-dry.log and never build/e181/session.log;
#   B  the session's gates refuse before any device: no gates set (8), T0 + 76 min past the end gate (8), E181_DESK without V3_DRY (2);
#   C  the measured pass through the block, F0 from the dry smoke's floor mark (0): the full design, by hold;
#   D  the start gate: G0-A6's room at 54.0 C (7); A8-4's residue at a 52.5 C room (7); the warm pattern at 52.0 C (0, H_E 2.60 s every
#      7.98 s); the room line's edge, a 53.9 C room with F0 53.5 C (0);
#   E  A6-1 at a 54.0 C floor: the smoke ends before its first launch (7, no launch);
#   F  a looser stop line refused; E181_DRY_ROOM_C and E181_DRY_FLOOR_C without --dry refused; the runner's --list (no tile problem);
#   G  no ssh, rsync or scp was called.
#
#   bash tools/claims-v3/e181/dry_intel_e181.sh <scratch dir> > <log>      (Intel only; GNU date as gdate on PATH)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
mkdir -p "$S"
S=$(cd "$S" && pwd -P)
T=$S/tree
B=$S/bin
rm -rf "${S:?}/tree" "${S:?}/bin"
mkdir -p "$T" "$B"
# the tree: step 7's sync list alone (s07_a3_sync_e181.sh: the kit directory and the box list's repo entries)
P=(tools/claims-v3/e181/)
while read -r _ p; do case "$p" in build/*|tools/claims-v3/e181/*) ;; *) P+=("$p") ;; esac; done < "$SRC/tools/claims-v3/e181/frozen-e181.sha256"
( cd "$SRC" && rsync -a -R --exclude __pycache__ "${P[@]}" "$T/" )
printf '#!/bin/sh\necho aifoundry3\n' > "$B/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$B/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$B/python3"
printf '#!/bin/sh\necho "(dry pass on the Intel: no et-who here)"\n' > "$B/et-who"
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused in a dry pass" >&2\nexit 97\n' "$n" "$S/network-calls.log" "$n" > "$B/$n"; done
: > "$S/network-calls.log"
chmod +x "$B"/*
export PATH="$B:$PATH"
cd "$T" || exit 2
fail=0
step() { echo; echo "== $*"; }
ok() { if [ "$1" = "$2" ]; then echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
clean() { sed "s#$T#<tree>#g; s#$S#<scratch>#g"; }
DD=build/claims-v3-dry/aifoundry3
echo "# E181's DRY-INTEL dry pass on the Intel, $(date '+%a %d %b %Y %H:%M:%S %Z'): V3_DRY=1 E181_DESK=1 in a tree built from step 7's sync list"
echo "# alone ($(( ${#P[@]} - 1 )) box-list files and tools/claims-v3/e181/; $(find "$T" -type f | wc -l | tr -d ' ') files); E97's toy card; no device, no ssh."
echo "# Shims on PATH: hostname -> aifoundry3, date -> GNU date, python3 -> /usr/bin/python3 ($(/usr/bin/python3 -V 2>&1)), et-who and network stand-ins."

step "A. the session: gates, the box list, the preflight, A6-1's floor mark, the smoke with its five stop tests, the smoke gate"
rm -rf build/e181 "$DD"
V3_DRY=1 E181_DESK=1 E181_T0=$(date +%s) E181_LATEST_START="$(date -d '+1 hour' '+%F %H:%M %Z')" E181_END_GATE="$(date -d '+3 hours' '+%F %H:%M %Z')" \
  bash tools/claims-v3/e181/session_e181.sh; rc=$?
echo "session rc=$rc"; cut -d' ' -f4- build/e181/session-dry.log | grep -vE '^\[aifoundry3\]|^[0-9]{2}:[0-9]{2}:[0-9]{2} ' | clean | cut -c1-240 | head -n 40
grep -m1 'floor F0 (A6-1' "$DD/e181-smoke/p18101/run.log" | cut -d' ' -f3- | clean
real=$([ -e build/e181/session.log ] && echo written || echo "not written")
fl=$(grep -c '"kind": "floor"' "$DD/e181-smoke/p18101/marks.jsonl" 2>/dev/null)
st=$(/usr/bin/python3 -c 'import json,sys; m=[json.loads(x) for x in open(sys.argv[1])]; s=[x for x in m if x.get("kind")=="stoptest"]; print(s[-1]["all_pass"] if s else None, json.dumps(s[-1]["results"]) if s else "")' "$DD/e181-smoke/p18101/marks.jsonl")
echo "the real log build/e181/session.log: $real; floor marks in the dry smoke: $fl; stop tests (all_pass, results): $st"
g=$(grep -c 'frozen-e181.sha256: every file as registered' build/e181/session-dry.log); bo=$(grep -c 'DESK: box-only, not checked here' build/e181/session-dry.log)
pf=$(grep -c 'dmcmd_audit preflight rc=0 (dmcmd_audit: GO' build/e181/session-dry.log); sg=$(grep -c 'the smoke or its gate failed: no measured pass' build/e181/session-dry.log)
ok "$rc.$g.$bo.$pf.$fl.$sg.$real" "0.1.3.1.1.1.not written" "session rc 0; box list clean (27 repo files) with 3 box-only binaries; preflight GO; one floor mark; the toy's smoke gate NO-GO; the real log untouched"

step "B. the session's gates refuse before any device"
rm -rf build/e181
V3_DRY=1 E181_DESK=1 E181_T0=$(date +%s) bash tools/claims-v3/e181/session_e181.sh; r1=$?
V3_DRY=1 E181_DESK=1 E181_T0=$(date +%s) E181_LATEST_START="$(date -d '+1 hour' '+%F %H:%M %Z')" E181_END_GATE="$(date -d '+60 min' '+%F %H:%M %Z')" \
  bash tools/claims-v3/e181/session_e181.sh; r2=$?
E181_DESK=1 E181_T0=$(date +%s) bash tools/claims-v3/e181/session_e181.sh 2>&1 | clean; r3=${PIPESTATUS[0]}
cut -d' ' -f4- build/e181/session-dry.log | clean | cut -c1-200
ok "$r1.$r2.$r3" "8.8.2" "no gates set 8; T0 + 76 min past the end gate 8; E181_DESK without V3_DRY 2"

FM=$DD/e181-smoke/p18101/marks.jsonl
step "C. the measured pass through the block, F0 from the dry smoke's floor mark (the toy's room 51.433 C: the cool pattern)"
rm -rf build/e181 "$DD/e181"
V3_DRY=1 E181_DESK=1 E181_FLOOR_MARKS="$FM" E181_DEADLINE_EPOCH=$(( $(date +%s) + 4500 )) bash tools/claims-v3/e181/block_e181.sh 18120 > "$S/c.out" 2>&1; rc=$?
echo "block 18120 rc=$rc"
grep -m1 '"kind": "start_gate"' "$DD/e181/p18120/marks.jsonl" | cut -c1-420
/usr/bin/python3 - "$DD/e181/p18120/marks.jsonl" <<'PY'
import json, sys
m = [json.loads(x) for x in open(sys.argv[1])]
holds = [x for x in m if x.get("kind") == "hold"]
launch = [x for x in m if x.get("kind") == "launch"]
rests = [x for x in m if x.get("kind") == "rest"]
plan = (max(x["t_end_ms"] for x in rests + holds) - min(x["t_start_ms"] for x in rests)) / 60000.0
for h in holds:
    ls = [x["t_start_ms"] for x in launch if x["block"] == h["name"]]
    per = (ls[-1] - ls[0]) / (len(ls) - 1) / 1000.0 if len(ls) > 1 else None
    print(f"  {h['name']}: {h['launches']} launches over {(h['t_end_ms'] - h['t_start_ms']) / 1000:.1f} s, start to start {per and round(per, 2)} s, ended {h['why_end']}")
order = [n for n, _ in sorted(((x["block"], x["t_start_ms"]) for x in launch), key=lambda y: y[1])]
seen = []
for n in order:
    if n not in seen:
        seen.append(n)
print(f"  plan {plan:.1f} min; the order by first launch {seen}; rests {[r['name'] for r in rests]}")
print("CHECK", len(holds) == 5 and seen == ["H_E", "Z", "L1", "S", "L2"] and abs(plan - 73.5) < 0.2)
PY
ck=$(/usr/bin/python3 - "$DD/e181/p18120/marks.jsonl" <<'PY'
import json, sys
m = [json.loads(x) for x in open(sys.argv[1])]
g = [x for x in m if x.get("kind") == "start_gate"][-1]
h = [x for x in m if x.get("kind") == "hold" and x["name"] == "H_E"][0]
print(int(g["passed"] is True and abs(g["floor_c"] - 51.43291) < 1e-4 and g["residue_pred_c"] == 0.414 and h["launches"] == 80))
PY
)
ok "$rc.$ck" "0.1" "the full design ran: passed, F0 the dry smoke's 51.433 C (the toy's code 1950), H_E 80 launches at the cool pattern"

step "D. the start gate on the toy: the room line, A8-4's residue line, the warm pattern, the room line's edge"
run_gate() {  # run_gate <pass> <room> [<floor override, no floor marks>]
  local p=$1 room=$2 fl=${3:-}
  rm -rf "$DD/e181/p$p"
  if [ -n "$fl" ]; then
    V3_DRY=1 E181_DESK=1 E181_DRY_ROOM_C=$room E181_DRY_FLOOR_C=$fl E181_DEADLINE_EPOCH=$(( $(date +%s) + 4500 )) bash tools/claims-v3/e181/block_e181.sh "$p" > "$S/d$p.out" 2>&1
  else
    V3_DRY=1 E181_DESK=1 E181_DRY_ROOM_C=$room E181_FLOOR_MARKS="$FM" E181_DEADLINE_EPOCH=$(( $(date +%s) + 4500 )) bash tools/claims-v3/e181/block_e181.sh "$p" > "$S/d$p.out" 2>&1
  fi
  local r=$?
  echo "  pass $p (room $room${fl:+, F0 $fl}): rc $r; $(grep -m1 'start gate (G0-A6' "$S/d$p.out" | cut -d' ' -f3- | cut -c1-200)"
  return $r
}
run_gate 18191 54.0; d1=$?
run_gate 18192 52.5; d2=$?
run_gate 18193 52.0; d3=$?
w=$(/usr/bin/python3 -c 'import json,sys; m=[json.loads(x) for x in open(sys.argv[1])]; h=[x for x in m if x.get("kind")=="hold_start" and x["name"]=="H_E"]; print(h[0]["launch_s"], h[0]["period_s"]) if h else print(None)' "$DD/e181/p18193/marks.jsonl")
echo "  pass 18193's H_E: $w (the warm pattern: 2.6 7.98)"
run_gate 18194 53.9 53.5; d4=$?
ok "$d1.$d2.$d3.$w.$d4" "7.7.0.2.6 7.98.0" "room 54.0 refused 7; residue at 52.5 refused 7; 52.0 runs the warm pattern; the 53.9 edge runs"

step "E. A6-1: a 54.0 C floor ends the smoke before its first launch"
rm -rf "$DD/e181-smoke/p18195"
V3_DRY=1 E181_DESK=1 E181_DRY_FLOOR_C=54.0 bash tools/claims-v3/e181/block_e181.sh 18195 --smoke > "$S/e.out" 2>&1; rc=$?
grep -m2 -E 'floor F0|STOP' "$S/e.out" | cut -d' ' -f3- | cut -c1-220
nl=$(grep -c '"kind": "launch"' "$DD/e181-smoke/p18195/marks.jsonl"); bj=$(grep -o '"status":"[a-z]*"' "$DD/e181-smoke/p18195/block.json")
ok "$rc.$nl.$bj" '7.0."status":"gate"' "exit 7, no launch, block status gate"

step "F. refusals and the runner's --list"
python3 tools/claims-v3/e181/run_e181.py /dev/null --root "$T" --hold-w 70 --list > "$S/f1.out" 2>&1; f1=$?; tail -n 1 "$S/f1.out"
E181_DRY_ROOM_C=52 python3 tools/claims-v3/e181/run_e181.py /dev/null --root "$T" --list > "$S/f2.out" 2>&1; f2=$?; tail -n 1 "$S/f2.out"
E181_DRY_FLOOR_C=52 python3 tools/claims-v3/e181/run_e181.py /dev/null --root "$T" --list > "$S/f3.out" 2>&1; f3=$?; tail -n 1 "$S/f3.out"
python3 tools/claims-v3/e181/run_e181.py /dev/null --root "$T" --list > "$S/f4.out" 2>&1; f4=$?
tp=$(/usr/bin/python3 -c 'import json,sys; j=json.load(open(sys.argv[1])); print(len(j["tile_problems"]), j["gates"])' "$S/f4.out")
echo "  --list: tile problems and gates: $tp"
ok "$f1.$f2.$f3.$f4.${tp%% *}" "1.1.1.0.0" "a looser stop line, the two dry overrides without --dry refused; --list rc 0, no tile problem"

step "G. no network call"
n=$(grep -c . "$S/network-calls.log"); echo "network stand-in calls: $n"
ok "$n" 0 "no ssh, rsync or scp"
rm -rf build/claims-v3-dry build/e181
echo
echo "DRY-INTEL $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
