#!/usr/bin/env bash
# E185 (M11's session 3): DRY-INTEL, the V3_DRY dry pass on the Intel (it never opens a device and never runs ssh), E185's dry_intel_e185.sh
# (33cdccf6, which stays as committed) ported, in a tree built FROM STEP 7'S SYNC LIST ALONE: tools/claims-v3/e185/ and every repo file of
# frozen-e185.sha256, nothing else (E174's defect class). The three box binaries are absent, as E185_DESK=1 lists them. The shims are E185's:
# hostname prints aifoundry3; date runs GNU date; python3 is the Intel's /usr/bin/python3; et-who prints a stand-in line; ssh, rsync and scp
# log the call and exit 97, so any network call fails the pass. With V3_DRY=1 E185_DESK=1 (E97's toy card: a virtual clock, a die that
# always reads 51 C, a 34-sensor mean of 51.433 C, a board that never rises):
#   A  the session: the gates, the box list (27 OK, 3 box-only listed), the preflight GO, A6-1's floor mark, the smoke with its six stop tests,
#      the smoke gate (NO-GO on the toy, expected); its files in build/e185/T<T0>-dry/ only (no real T0 directory, no LAST_T0), and its
#      MANIFEST.sha256 reads back clean;
#   B  the session's gates refuse before any device: no gates set (8), T0 + 105 min past the end gate (8), E185_DESK without V3_DRY (2), a T0
#      directory that exists already (8);
#   C  the measured pass through the block, F0 from the dry smoke's floor mark (0): E185.md section 4's six holds in the seed's order, the
#      plan's length, H_E and H_E2 each 80 launches at the cool pattern;
#   D  the start gate: G0-A6's room at 54.0 C (7); A8-4's residue at a 52.5 C room (7); the warm pattern at 52.0 C on H_E and H_E2 (0); the
#      room line's edge, a 53.9 C room with F0 53.5 C (0);
#   E  A6-1 at a 54.0 C floor: the smoke ends before its first launch (7, no launch);
#   F  a looser stop line refused (the 72 C firmware hold line, the 70 W board line); the dry overrides without --dry refused; the runner's
#      --list (no tile problem; the lines printed);
#   S  E185's stops: a stricter 34-sensor-mean hold line of 51 C on the toy (its mean 51.433 C) ends H_E and the pass (6), and no later hold
#      starts;
#   G  no ssh, rsync or scp was called.
#
#   bash tools/claims-v3/e185/dry_intel_e185.sh <scratch dir> > <log>      (Intel only; GNU date as gdate on PATH)
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
# the tree: step 7's sync list alone (s07_a3_sync_e185.sh: the kit directory and the box list's repo entries)
P=(tools/claims-v3/e185/)
while read -r _ p; do case "$p" in build/*|tools/claims-v3/e185/*) ;; *) P+=("$p") ;; esac; done < "$SRC/tools/claims-v3/e185/frozen-e185.sha256"
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
echo "# E185's DRY-INTEL dry pass on the Intel, $(date '+%a %d %b %Y %H:%M:%S %Z'): V3_DRY=1 E185_DESK=1 in a tree built from step 7's sync list"
echo "# alone ($(( ${#P[@]} - 1 )) box-list files and tools/claims-v3/e185/; $(find "$T" -type f | wc -l | tr -d ' ') files); E97's toy card; no device, no ssh."
echo "# Shims on PATH: hostname -> aifoundry3, date -> GNU date, python3 -> /usr/bin/python3 ($(/usr/bin/python3 -V 2>&1)), et-who and network stand-ins."

step "A. the session: gates, the box list, the preflight, A6-1's floor mark, the smoke with its six stop tests, the smoke gate, T0-named files"
rm -rf build/e185 "$DD"
T0A=$(date +%s); SDA=build/e185/T$T0A-dry; LA=$SDA/session-dry.log
V3_DRY=1 E185_DESK=1 E185_T0=$T0A E185_LATEST_START="$(date -d '+1 hour' '+%F %H:%M %Z')" E185_END_GATE="$(date -d '+3 hours' '+%F %H:%M %Z')" \
  bash tools/claims-v3/e185/session_e185.sh; rc=$?
echo "session rc=$rc"; cut -d' ' -f4- "$LA" | grep -vE '^\[aifoundry3\]|^[0-9]{2}:[0-9]{2}:[0-9]{2} ' | clean | cut -c1-240 | head -n 40
grep -m1 'floor F0 (A6-1' "$DD/e185-smoke/p18501/run.log" | cut -d' ' -f3- | clean
real=$([ -e "build/e185/T$T0A" ] && echo written || echo "not written")
lt=$([ -e build/e185/LAST_T0 ] && echo written || echo none)
mf=$( (sha256sum -c --quiet "$SDA/MANIFEST.sha256" > "$S/a-manifest.out" 2>&1 && [ "$(grep -c . "$SDA/MANIFEST.sha256")" -gt 5 ]) && echo clean || echo DIFFERS)
echo "the T0 directory's manifest: $(grep -c . "$SDA/MANIFEST.sha256" 2>/dev/null) files, $mf"
st6=$(/usr/bin/python3 - "$DD/e185-smoke/p18501/marks.jsonl" <<'PY'
import json, sys
m = [json.loads(x) for x in open(sys.argv[1])]
s = [x for x in m if x.get("kind") == "stoptest"]
r = s[-1]["results"] if s else {}
want = {"gate", "hold_die", "hold_die34", "hold_board", "in_launch", "session"}
# on the toy, the 34-sensor-mean line and the in-launch board line cannot fire (its newest sample has no 34 codes, its board never rises)
toy_ok = {k for k, v in r.items() if v.get("pass")} == want - {"hold_die34", "in_launch"}
print(f"{len(r)}.{int(set(r) == want and toy_ok)}")
PY
)
fl=$(grep -c '"kind": "floor"' "$DD/e185-smoke/p18501/marks.jsonl" 2>/dev/null)
st=$(/usr/bin/python3 -c 'import json,sys; m=[json.loads(x) for x in open(sys.argv[1])]; s=[x for x in m if x.get("kind")=="stoptest"]; print(s[-1]["all_pass"] if s else None, json.dumps(s[-1]["results"]) if s else "")' "$DD/e185-smoke/p18501/marks.jsonl")
echo "a real T0 directory build/e185/T$T0A: $real; LAST_T0: $lt; floor marks in the dry smoke: $fl; stop tests (all_pass, results): $st"
g=$(grep -c 'frozen-e185.sha256: every file as registered' "$LA"); bo=$(grep -c 'DESK: box-only, not checked here' "$LA")
pf=$(grep -c 'dmcmd_audit preflight rc=0 (dmcmd_audit: GO' "$LA"); sg=$(grep -c 'the smoke or its gate failed: no measured pass' "$LA")
ok "$rc.$g.$bo.$pf.$fl.$sg.$real.$st6.$mf.$lt" "0.1.3.1.1.1.not written.6.1.clean.none" "session rc 0; box list clean (27 repo files) with 3 box-only binaries; preflight GO; one floor mark; the toy's smoke gate NO-GO; no real T0 directory; the six stop tests run, the four the toy can fire passed; its manifest reads back; no LAST_T0"

step "B. the session's gates refuse before any device"
rm -rf build/e185
t=$(date +%s); V3_DRY=1 E185_DESK=1 E185_T0=$t bash tools/claims-v3/e185/session_e185.sh; r1=$?
V3_DRY=1 E185_DESK=1 E185_T0=$((t + 1)) E185_LATEST_START="$(date -d '+1 hour' '+%F %H:%M %Z')" E185_END_GATE="$(date -d '+100 min' '+%F %H:%M %Z')" \
  bash tools/claims-v3/e185/session_e185.sh; r2=$?
E185_DESK=1 E185_T0=$((t + 2)) bash tools/claims-v3/e185/session_e185.sh 2>&1 | clean; r3=${PIPESTATUS[0]}
V3_DRY=1 E185_DESK=1 E185_T0=$t E185_LATEST_START="$(date -d '+1 hour' '+%F %H:%M %Z')" E185_END_GATE="$(date -d '+3 hours' '+%F %H:%M %Z')" \
  bash tools/claims-v3/e185/session_e185.sh 2>&1 | clean; r4=${PIPESTATUS[0]}
cut -d' ' -f4- build/e185/T$t-dry/session-dry.log build/e185/T$((t + 1))-dry/session-dry.log | clean | cut -c1-200
ok "$r1.$r2.$r3.$r4" "8.8.2.8" "no gates set 8; T0 + 105 min past the end gate 8; E185_DESK without V3_DRY 2; a T0 directory that exists already 8"

FM=$DD/e185-smoke/p18501/marks.jsonl
step "C. the measured pass through the block, F0 from the dry smoke's floor mark (the toy's room 51.433 C: the cool pattern)"
rm -rf build/e185 "$DD/e185"
V3_DRY=1 E185_DESK=1 E185_FLOOR_MARKS="$FM" E185_DEADLINE_EPOCH=$(( $(date +%s) + 6240 )) bash tools/claims-v3/e185/block_e185.sh 18520 > "$S/c.out" 2>&1; rc=$?
echo "block 18520 rc=$rc"
grep -m1 '"kind": "start_gate"' "$DD/e185/p18520/marks.jsonl" | cut -c1-420
/usr/bin/python3 - "$DD/e185/p18520/marks.jsonl" <<'PY'
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
print("CHECK", len(holds) == 6 and seen == ["H_E", "L1", "L2", "H_E2", "S", "S2"] and abs(plan - 101.0) < 0.3)
PY
ck=$(/usr/bin/python3 - "$DD/e185/p18520/marks.jsonl" <<'PY'
import json, sys
m = [json.loads(x) for x in open(sys.argv[1])]
g = [x for x in m if x.get("kind") == "start_gate"][-1]
h = [x for x in m if x.get("kind") == "hold" and x["name"] == "H_E"][0]
h2 = [x for x in m if x.get("kind") == "hold" and x["name"] == "H_E2"][0]
rests = [x for x in m if x.get("kind") == "rest"]
seen = []
for x in sorted((x for x in m if x.get("kind") == "launch"), key=lambda y: y["t_start_ms"]):
    if x["block"] not in seen:
        seen.append(x["block"])
plan = (max(x["t_end_ms"] for x in rests) - min(x["t_start_ms"] for x in rests)) / 60000.0
print(int(g["passed"] is True and abs(g["floor_c"] - 51.43291) < 1e-4 and g["residue_pred_c"] == 0.414 and h["launches"] == 80
          and h2["launches"] == 80 and seen == ["H_E", "L1", "L2", "H_E2", "S", "S2"] and abs(plan - 101.0) < 0.3))
PY
)
ok "$rc.$ck" "0.1" "the full design ran: passed, F0 the dry smoke's 51.433 C (the toy's code 1950), the seed's order, about 101 minutes, H_E and H_E2 80 launches each at the cool pattern"

step "D. the start gate on the toy: the room line, A8-4's residue line, the warm pattern, the room line's edge"
run_gate() {  # run_gate <pass> <room> [<floor override, no floor marks>]
  local p=$1 room=$2 fl=${3:-}
  rm -rf "$DD/e185/p$p"
  if [ -n "$fl" ]; then
    V3_DRY=1 E185_DESK=1 E185_DRY_ROOM_C=$room E185_DRY_FLOOR_C=$fl E185_DEADLINE_EPOCH=$(( $(date +%s) + 6240 )) bash tools/claims-v3/e185/block_e185.sh "$p" > "$S/d$p.out" 2>&1
  else
    V3_DRY=1 E185_DESK=1 E185_DRY_ROOM_C=$room E185_FLOOR_MARKS="$FM" E185_DEADLINE_EPOCH=$(( $(date +%s) + 6240 )) bash tools/claims-v3/e185/block_e185.sh "$p" > "$S/d$p.out" 2>&1
  fi
  local r=$?
  echo "  pass $p (room $room${fl:+, F0 $fl}): rc $r; $(grep -m1 'start gate (G0-A6' "$S/d$p.out" | cut -d' ' -f3- | cut -c1-200)"
  return $r
}
run_gate 18591 54.0; d1=$?
run_gate 18592 52.5; d2=$?
run_gate 18593 52.0; d3=$?
w=$(/usr/bin/python3 - "$DD/e185/p18593/marks.jsonl" <<'PY'
import json, sys
m = [json.loads(x) for x in open(sys.argv[1])]
h = [x for x in m if x.get("kind") == "hold_start" and x["name"] in ("H_E", "H_E2")]
print(" ".join(sorted({f"{x['launch_s']} {x['period_s']}" for x in h})) if len(h) == 2 else None)
PY
)
echo "  pass 18593's H_E and H_E2: $w (the warm pattern on both: 2.6 7.98)"
run_gate 18594 53.9 53.5; d4=$?
ok "$d1.$d2.$d3.$w.$d4" "7.7.0.2.6 7.98.0" "room 54.0 refused 7; residue at 52.5 refused 7; 52.0 runs the warm pattern on H_E and H_E2; the 53.9 edge runs"

step "E. A6-1: a 54.0 C floor ends the smoke before its first launch"
rm -rf "$DD/e185-smoke/p18595"
V3_DRY=1 E185_DESK=1 E185_DRY_FLOOR_C=54.0 bash tools/claims-v3/e185/block_e185.sh 18595 --smoke > "$S/e.out" 2>&1; rc=$?
grep -m2 -E 'floor F0|STOP' "$S/e.out" | cut -d' ' -f3- | cut -c1-220
nl=$(grep -c '"kind": "launch"' "$DD/e185-smoke/p18595/marks.jsonl"); bj=$(grep -o '"status":"[a-z]*"' "$DD/e185-smoke/p18595/block.json")
ok "$rc.$nl.$bj" '7.0."status":"gate"' "exit 7, no launch, block status gate"

step "F. refusals and the runner's --list"
python3 tools/claims-v3/e185/run_e185.py /dev/null --root "$T" --hold-w 70 --list > "$S/f1.out" 2>&1; f1=$?; tail -n 1 "$S/f1.out"
python3 tools/claims-v3/e185/run_e185.py /dev/null --root "$T" --hold-c 72 --list > "$S/f1b.out" 2>&1; f1b=$?; tail -n 1 "$S/f1b.out"
E185_DRY_ROOM_C=52 python3 tools/claims-v3/e185/run_e185.py /dev/null --root "$T" --list > "$S/f2.out" 2>&1; f2=$?; tail -n 1 "$S/f2.out"
E185_DRY_FLOOR_C=52 python3 tools/claims-v3/e185/run_e185.py /dev/null --root "$T" --list > "$S/f3.out" 2>&1; f3=$?; tail -n 1 "$S/f3.out"
python3 tools/claims-v3/e185/run_e185.py /dev/null --root "$T" --list > "$S/f4.out" 2>&1; f4=$?
tp=$(/usr/bin/python3 -c 'import json,sys; j=json.load(open(sys.argv[1])); print(len(j["tile_problems"]), j["gates"], j["lines"])' "$S/f4.out")
echo "  --list: tile problems, gates and lines: $tp"
ok "$f1.$f1b.$f2.$f3.$f4.${tp%% *}" "1.1.1.1.0.0" "a looser board line and a looser firmware line, the two dry overrides without --dry refused; --list rc 0, no tile problem"

step "S. E185's stops: a stricter 34-sensor-mean hold line (51 C) on a toy whose newest sample carries 34 codes (mean 51.433 C) ends H_E and the pass"
rm -rf "$S/s-pass"
cat > "$S/s_wrap.py" <<'PY'
import os, runpy, sys
sys.path.insert(0, os.path.join("tools", "claims-v3", "e97"))
import run_e97b as b
orig = b.DryCard.latest
def latest(self):
    r = orig(self)
    r["pvt"] = {"st": 0, "f": 0, "c": [1950] * 34}      # the toy's tail() codes, on its newest sample too (this test only)
    return r
b.DryCard.latest = latest
sys.argv = ["run_e185.py"] + sys.argv[1:]
runpy.run_path(os.path.join("tools", "claims-v3", "e185", "run_e185.py"), run_name="__main__")
PY
V3_DRY=1 E185_DRY_FLOOR_C=51.0 /usr/bin/python3 -B "$S/s_wrap.py" "$S/s-pass" --root "$T" --dry --hold-m34-c 51.0 --pass-no 18596 \
  --deadline-epoch $(( $(date +%s) + 6240 )) > "$S/s.out" 2>&1; rs=$?
grep -E 'STOP|decision' "$S/s-pass/run.log" | cut -d' ' -f3- | cut -c1-220 | head -n 4
sk=$(/usr/bin/python3 - "$S/s-pass/marks.jsonl" <<'PY'
import json, sys
m = [json.loads(x) for x in open(sys.argv[1])]
hs = [x["name"] for x in m if x.get("kind") == "hold_start"]
he = [x for x in m if x.get("kind") == "hold" and x["name"] == "H_E"]
w = [x for x in m if x.get("kind") == "watch"]
print(int(hs == ["H_E"] and he and he[0]["why_end"] == "stop" and w and w[0]["rule"] == "die34"))
PY
)
ok "$rs.$sk" "6.1" "exit 6; H_E ended on the die34 line, and no later hold started (a stop ends the pass)"

step "G. no network call"
n=$(grep -c . "$S/network-calls.log"); echo "network stand-in calls: $n"
ok "$n" 0 "no ssh, rsync or scp"
rm -rf build/claims-v3-dry build/e185
echo
echo "DRY-INTEL $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
