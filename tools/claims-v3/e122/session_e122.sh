#!/usr/bin/env bash
# E122 (Q134): the card session on aifoundry3 card 0, detached on the box right after the claim edit (run from ~/aifoundry):
#
#   E122_T0=<claim epoch> setsid nohup bash tools/claims-v3/e122/session_e122.sh > build/e122-session.log 2>&1 < /dev/null &
#
# 1. et-who (the card must be free) and the session-start `ettelem config` (read only, under the card lock, timeout 10);
# 2. the smoke, pass 12201: tools/claims-v3/signloc/block_e108.sh 12201 --smoke, unchanged (E108's eight 2 s runs at the
#    current reading), and its gate (the block ended ok; all eight items ran; every run ok on 1,024 minions; cycles per op
#    within 0.5% of 546; both config reads TDP 0 W, threshold 65 C, 600 MHz). No read-back and no pass if it fails;
# 3. the read-back, pass 12202: block_readback_e122.sh (E108's 96 reads with E116's read-back host). A failed read is
#    recorded and the session goes on: the power passes do not depend on it;
# 4. the measured passes 12210-12213, block_e108.sh unchanged, one after another: a pass starts only if
#    now + projected <= E122_T0 + 2400 - 240 s and <= 2026-11-01 23:15 PST, where projected is the longest pass so far,
#    450 s until one has ended. A pass in flight is never cut; build/claims-v3/STOP or build/e122-STOP stops before the
#    next; a pass that found another user (exit 3) is retried once after 5 min if that still fits; any other failure stops;
# 5. et-who and the session-end `ettelem config` (read only, under the card lock), unless another process holds the card.
# Nothing is set: no governor, TDP, threshold or clock write, no reset, no --reset-ms, no PMIC command.
# E122_STUB=1 (run_e122.sh setup only): every block is a 3 s sleep, no device is opened, the gate is skipped.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE
T0=${E122_T0:?E122_T0 - the time of the claim edit, epoch seconds}
BUDGET_S=${E122_BUDGET_S:-2400}; RESERVE_S=${E122_RESERVE_S:-240}; GAP_S=${E122_GAP_S:-15}
longest=${E122_FIRST_S:-450}; done_n=0
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E122_DEADLINE:-2026-11-01 23:15 PST}" +%s)
STUB=${E122_STUB:-}
L=build/e122-logs; [ -n "$STUB" ] && L=build/e122-stub-logs
mkdir -p "$L"
SL=tools/claims-v3/signloc
PASSES="12210 12211 12212 12213"   # predictions-e122.json > plan > passes_planned
say() { echo "$(date '+%F %T %Z') $*"; }
rel() { echo "T0+$(( $1 - T0 )) s"; }
blk() { if [ -n "$STUB" ]; then sleep 3; return 0; fi; bash "$@" < /dev/null; }
cfg() {
  [ -n "$STUB" ] && { echo '{"stub":true}' > "$1"; return 0; }
  flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null 2>/dev/null | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
endread() {
  local w
  w=$(timeout 20 et-who 2>&1 | head -5)
  say "et-who: $w"
  if [ -n "$STUB" ] || printf '%s' "$w" | grep -q 'No process holds'; then cfg "$L/config-session-end.json"
  else say "session-end config: not read (the card is not free)"; fi
}
say "session start: T0 $(date -d @"$T0" +%T), last pass end by $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T)${STUB:+ (STUB)}"
w=$(timeout 20 et-who 2>&1 | head -5)
say "et-who: $w"
if [ -z "$STUB" ] && ! printf '%s' "$w" | grep -q 'No process holds'; then say "the card is not free: no block runs"; say "session done"; exit 3; fi
say "logins: $(who | wc -l) (names not recorded)"
cfg "$L/config-session-start.json"

say "smoke 12201 starts"
blk $SL/block_e108.sh 12201 --smoke > "$L/smoke.log" 2>&1; rc=$?
say "smoke rc=$rc"
if [ -n "$STUB" ]; then gate="PASS (stub)"; else
gate=$(python3 - build/claims-v3/aifoundry3/signloc-smoke/p12201 <<'PYEOF'
import json, os, sys, collections
d = sys.argv[1]
why = []
try:
    b = json.load(open(os.path.join(d, "block.json")))
    if b.get("status") != "ok":
        why.append(f"block status {b.get('status')}")
except (OSError, ValueError) as e:
    why.append(f"block.json: {e}")
runs = []
try:
    runs = [json.loads(l) for l in open(os.path.join(d, "runs.jsonl")) if l.strip().startswith("{")]
except OSError as e:
    why.append(f"runs.jsonl: {e}")
want = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
for r in runs:
    if not r.get("ok"):
        why.append(f"{r.get('item')} not ok")
    if r.get("minions") != 1024:
        why.append(f"{r.get('item')} minions {r.get('minions')}")
    c = r.get("cycles_per_op")
    if c is None or abs(c / want.get(r.get("type"), 1e9) - 1) > 0.005:
        why.append(f"{r.get('item')} cycles/op {c}")
need = set(json.load(open("tools/claims-v3/signloc/e108/e108.json"))["smoke"])
items = {r.get("item") for r in runs}
if not need <= items:
    why.append(f"smoke items missing: {sorted(need - items)}")
for nm in ("config_start", "config_end"):
    try:
        c = json.load(open(os.path.join(d, nm + ".json")))
        if (c.get("tdp_w"), c.get("temp_threshold_c"), c.get("minion_mhz")) != (0, 65, 600):
            why.append(f"{nm} reads {c.get('tdp_w')}/{c.get('temp_threshold_c')} at {c.get('minion_mhz')} MHz, not 0/65 at 600")
    except (OSError, ValueError) as e:
        why.append(f"{nm}: {e}")
cpo = sorted({round(r.get("cycles_per_op") or 0, 1) for r in runs})
print(("PASS" if not why else "FAIL"), f"{len(runs)} runs, {len(items)} items, cycles/op {cpo};", "; ".join(why[:6]))
PYEOF
)
fi
say "smoke gate: $gate"
if [ "${gate%% *}" != PASS ]; then
  say "no read-back and no pass: the smoke gate failed"
  endread; say "session done at $(rel "$(date +%s)")"; exit 1
fi

say "read-back 12202 starts"
blk tools/claims-v3/e122/block_readback_e122.sh 12202 > "$L/readback.log" 2>&1; rc=$?
say "read-back rc=$rc: $(tail -1 "$L/readback.log" 2>/dev/null | cut -c1-160)"

for p in $PASSES; do
  for f in build/claims-v3/STOP build/e122-STOP; do [ -e "$f" ] && { say "$f exists: stopping before p$p"; break 2; }; done
  now=$(date +%s)
  if [ $((now + longest)) -gt "$limit" ] || [ $((now + longest)) -gt "$deadline" ]; then
    say "budget: stopping before p$p (now $(rel "$now"), projected ${longest} s, ends $(rel $((now + longest))) > $(rel "$limit"))"
    break
  fi
  say "p$p starts at $(rel "$now") (projected ${longest} s, end by $(rel $((now + longest))))"
  t0=$(date +%s)
  blk $SL/block_e108.sh "$p" >> "$L/passes.log" 2>&1; rc=$?
  say "p$p rc=$rc ($(( $(date +%s) - t0 )) s)"
  if [ $rc -eq 3 ]; then
    sleep 300
    now=$(date +%s)
    if [ $((now + longest)) -le "$limit" ] && [ $((now + longest)) -le "$deadline" ]; then
      t0=$(date +%s)
      blk $SL/block_e108.sh "$p" >> "$L/passes.log" 2>&1; rc=$?
      say "p$p retry rc=$rc"
    else
      say "budget: no retry of p$p"; break
    fi
  fi
  [ $rc -eq 0 ] || { say "stopping after p$p (rc $rc)"; break; }
  d=$(( $(date +%s) - t0 ))
  { [ "$done_n" -eq 0 ] || [ $d -gt "$longest" ]; } && longest=$d   # the estimate holds until the first pass ends
  done_n=$((done_n + 1))
  sleep "$GAP_S"
done
say "passes done: $done_n"
endread
say "session done at $(rel "$(date +%s)")"
