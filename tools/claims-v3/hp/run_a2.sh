#!/usr/bin/env bash
# Heat placement (HP): aifoundry2's same-day session (DESIGN2 §3.5) starts here, never at a2/block.sh directly:
#
#   cd ~/claude/et-soc1-heat && bash tools/claims-v3/hp/run_a2.sh <attempt 1-4>
#   V3_DRY=1 HP_DRY_REST=61 bash tools/claims-v3/hp/run_a2.sh 1          (dry: the simulator)
#
# a2/ is frozen in PREREG-A2 (its data exist), so the fixes of the 27 Sep re-verification that concern a2 live here,
# in front of it; they only refuse or delay, and change nothing a2/block.sh does once it starts. Refused (exit 2,
# recorded in build/claims-v3[-dry]/hp-refused.jsonl):
#  - any host but aifoundry2;
#  - V3_FORCE without V3_DRY=1: lib.sh's block_begin would re-run a finished attempt into its own directory (runs and
#    telemetry overwritten), which also repeats attempt 1 at once, past PREREG-A2's 2 h gap and re-check limit (review
#    medium). An attempt whose directory already holds block.json is refused as well (without V3_FORCE lib.sh would
#    only say "already done");
#  - HP_HEATER, HP_BIN_ROOT, HP_ETTELEM, HP_ETTELEM_HP without V3_DRY unless they resolve to the default binaries: the
#    lock hashes build/sparsity_t2/kernel/sparsity.elf, but the frozen a2 code launches the heater without --kernel,
#    so a relocated heater would load its compiled-in kernel instead (review low);
#  - a cool-down (review low): after an ABORTED attempt that launched anything, the next attempt waits until 30 min
#    (DESIGN2 §4.4's session gap, hplib.py session_gap_s) after that attempt's end, so the re-check's rest reading R is
#    not taken on a die still warm from our own aborted runs. PREREG-A2 lets a re-check follow an abort at once; this
#    only delays it. HP_A2_NO_COOL skips the wait under V3_DRY only (dry tests).
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT"
host=$(hostname)
DRYD=; [ -n "${V3_DRY:-}" ] && DRYD=-dry
LOGF=$ROOT/build/claims-v3$DRYD/hp-refused.jsonl
A2D=$ROOT/build/claims-v3$DRYD/aifoundry2/hp/a2
att=${1:-}
refuse() {
  mkdir -p "$(dirname "$LOGF")"
  python3 -c 'import json,sys,time; print(json.dumps({"t_ms": int(time.time()*1000), "who": "run_a2.sh", "host": sys.argv[1],
    "attempt": sys.argv[2], "why": sys.argv[3], "dry": bool(sys.argv[4])}))' "$host" "$att" "$1" "${V3_DRY:-}" >> "$LOGF" 2>/dev/null || true
  echo "$(date +%FT%T) run_a2.sh: $1: refused" >&2
  exit 2
}
[ "$host" = aifoundry2 ] || refuse "the a2 session runs on aifoundry2 only (this is $host)"
case "$att" in 1|2|3|4) ;; *) refuse "usage: run_a2.sh <attempt 1-4>" ;; esac
if [ -z "${V3_DRY:-}" ]; then
  [ -n "${V3_FORCE:-}" ] && refuse "V3_FORCE is honoured only under V3_DRY=1 (it would re-run a finished attempt into its own directory)"
  [ -n "${HP_A2_NO_COOL:-}" ] && refuse "HP_A2_NO_COOL is honoured only under V3_DRY=1"
  for v in HP_BIN_ROOT:build HP_HEATER:build/sparsity_t2/host/sparsity_host HP_ETTELEM:build/ettelem/ettelem \
           HP_ETTELEM_HP:build/ettelem-hp/ettelem; do
    name=${v%%:*}; def=${v#*:}; val=${!name:-}
    [ -z "$val" ] && continue
    [ "$(realpath -m "$val")" = "$(realpath -m "$ROOT/$def")" ] ||
      refuse "$name=$val is not the locked default $def (the frozen a2 code does not pass --kernel: a relocated heater loads its compiled-in kernel)"
  done
fi
if [ -e "$A2D/p$att/block.json" ] && [ -z "${V3_FORCE:-}" ]; then
  refuse "attempt $att already ran ($A2D/p$att/block.json): an attempt is never re-run"
fi
# the cool-down after an ABORTED attempt that launched anything
now=$(date +%s%3N)
if [ -n "${V3_DRY:-}" ]; then        # the dry simulator's virtual clock (hplib.sh keeps it in the sim directory)
  sd=${HP_DRY_DIR:-$ROOT/build/claims-v3-dry/hp-sim}
  [ -s "$sd/vt0" ] && now=$(V3_DRY=1 HP_VT0=$(cat "$sd/vt0") HP_DRY_SPEED=${HP_DRY_SPEED:-40} python3 tools/claims-v3/hp/hplib.py vnow)
fi
gap=$(python3 -c 'import sys; sys.path.insert(0, "tools/claims-v3/hp"); import hplib; print(int(hplib.DEFAULTS["session_gap_s"]))')
cool=$(python3 - "$A2D" "$now" "$gap" <<'PY'
import glob, json, os, sys
d, now, gap = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
last = None
for bj in glob.glob(os.path.join(d, "p*", "block.json")):
    try:
        b = json.load(open(bj))
    except Exception:
        continue
    if last is None or (b.get("t1_ms") or 0) > (last[1].get("t1_ms") or 0):
        last = (os.path.dirname(bj), b)
if last:
    p, b = last
    try:
        a = json.load(open(os.path.join(p, "a2.json")))
    except Exception:
        a = {}
    lj = os.path.join(p, "launches.jsonl")
    launched = os.path.exists(lj) and os.path.getsize(lj) > 0
    left = (b.get("t1_ms") or 0) + gap * 1000 - now
    if a.get("branch") == "ABORTED" and launched and left > 0:
        print("%s ABORTED at %s after launching: %d s of the %d s cool-down left" % (os.path.basename(p), b.get("t1_ms"), left // 1000 + 1, gap))
PY
)
if [ -n "$cool" ]; then
  if [ -n "${V3_DRY:-}" ] && [ -n "${HP_A2_NO_COOL:-}" ]; then echo "$(date +%FT%T) run_a2.sh: dry: cool-down skipped (HP_A2_NO_COOL): $cool"
  else refuse "cool-down after an aborted attempt: $cool (re-run this attempt later)"; fi
fi
echo "$(date +%FT%T) run_a2.sh: attempt $att on $host: checks passed; exec a2/block.sh${V3_FORCE:+ (V3_FORCE, dry)}"
exec bash "$ROOT/tools/claims-v3/hp/a2/block.sh" "$@"
