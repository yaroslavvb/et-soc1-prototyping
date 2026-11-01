#!/usr/bin/env bash
# E118's card session on aifoundry1 card 0, run DETACHED by `run_e118.sh session` after the gates passed and the GO was
# committed. In order: the pin (watchdog armed first) -> the pinned smoke (every sample at 600 MHz or the pin failed)
# -> the launch-reading probe -> the 600 MHz passes (5 planned, 3 the minimum, inside the card-time cap) -> SP ring
# dump -> the restore (always, also from the trap) and its read-back -> the return burst -> SP ring dump -> the
# 800 MHz control (3 planned, 2 the minimum) -> closing reads. The envelope guard runs throughout.
# Every card touch goes through block_e118.sh (lib.sh: the card lock, timeout 10 per device process, the other-user
# test) or gov_e118.py (the locks, timeout 20 per call). Nothing here resets, reboots, rescans or unloads anything.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
export V3_DEVICE=0 ET_DEVICES=0 LD_LIBRARY_PATH=/opt/et/lib
K=tools/claims-v3/e118
S=$ROOT/build/e118
CAP_END=${E118_CAP_END:?epoch by which every card step ends}
export HL_GEN=${HL_GEN:-$ROOT/build/hl-gen} HL_MAX_C=72
ITEMS600=anchor_pi,anchor_ones,anchor_zeros,anchor_randn,lq_h0,lq_h1,lq_h2,lq_h4,lq_h8,lq_h12,lq_h16,lq_h23,lb_h0,lb_h1,lb_h2,lb_h4,lb_h8,lb_h12,lb_h16,lb_h23
CUT1=anchor_pi,anchor_ones,anchor_randn,lq_h0,lq_h1,lq_h2,lq_h4,lq_h8,lq_h12,lq_h16,lq_h23,lb_h0,lb_h1,lb_h2,lb_h4,lb_h8,lb_h23
ITEMSC=anchor_pi,lq_h0,lq_h2,lq_h8
D=$ROOT/build/claims-v3/aifoundry1-c0
mkdir -p "$S"
log() { echo "$(date '+%F %T %Z') $*" >> "$S/session.log"; }
step() { echo "{\"t_ms\":$(date +%s%3N),\"step\":\"$1\",\"rc\":${2:-null},\"note\":\"${3:-}\"}" >> "$S/steps.jsonl"; }
PINNED=0; GUARD=
restore_now() {
  rm -f "$S/pinned"
  python3 -I $K/gov_e118.py restore --out "$S" >> "$S/session.log" 2>&1; local rc=$?
  step restore "$rc"
  [ $rc -eq 0 ] && PINNED=0
  return $rc
}
finish() {
  [ "$PINNED" = 1 ] && { log "finish: TDP 0 may be set: restoring"; restore_now; }
  [ -n "$GUARD" ] && kill -TERM "$GUARD" 2>/dev/null
  GUARD=
}
trap 'log "signal"; finish; step trapped 1; echo "{\"status\":\"signal\"}" > "$S/end.json"; exit 1' TERM INT HUP
left() { echo $(( CAP_END - $(date +%s) )); }
hl() {  # hl <expn> <pass> <items> [--smoke] [VAR=value ...]; returns block_e118.sh's rc
  local expn=$1 pass=$2 items=$3 smoke=; shift 3
  if [ "${1:-}" = --smoke ]; then smoke=--smoke; shift; fi
  env HL_EXPN="$expn" "$@" bash $K/block_e118.sh "$pass" "$items" $smoke >> "$S/session.log" 2>&1 < /dev/null
}
only600() {  # the histogram has samples, all at 600 MHz
  python3 -c 'import json,sys; h=json.loads(sys.argv[1]); sys.exit(0 if h and set(h)=={"600"} else 1)' "$1"
}
reached() {  # every run mark of a pass on protocol, and no skipped mark
  python3 - "$1/marks.jsonl" <<'PY'
import json, sys
m = [json.loads(l) for l in open(sys.argv[1]) if l.startswith("{")]
runs = [x for x in m if x.get("kind") == "run"]
skip = [x for x in m if x.get("kind") == "skipped"]
sys.exit(0 if runs and not skip and all(x.get("on_protocol") for x in runs) else 1)
PY
}
clock_hist() {  # MHz histogram of a finished pass's telemetry
  python3 - "$1" <<'PY'
import gzip, json, os, sys
p = os.path.join(sys.argv[1], "telemetry.jsonl.gz")
p = p if os.path.exists(p) else p[:-3]
h = {}
op = gzip.open if p.endswith(".gz") else open
for l in op(p, "rt"):
    if l.startswith("{"):
        try:
            m = json.loads(l)["mhz"]["minion"]
        except Exception:
            continue
        h[m] = h.get(m, 0) + 1
print(json.dumps(h))
PY
}

log "session start; cap end $(date -d @"$CAP_END" '+%T %Z'), $(left) s left"
sha256sum $K/*.py $K/*.sh tools/claims-v3/hl/run_hl.py tools/claims-v3/lib.sh build/ettelem-e118/ettelem \
  build/sparsity/host/sparsity_host build/sparsity/kernel/sparsity.elf > "$S/code.sha256" 2>&1
rm -f "$S/STOP" build/hl-STOP
python3 -I $K/guard_e118.py --root "$ROOT" --session "$S" > /dev/null 2>&1 < /dev/null &
GUARD=$!
step guard_started 0 "$GUARD"

# ---- 1. the pin ---------------------------------------------------------------------------------------------------
PINNED=1   # from here a failure restores (the set may have landed even if its rc says otherwise)
python3 -I $K/gov_e118.py pin --out "$S" --deadline-s 4500 >> "$S/session.log" 2>&1; rc=$?
step pin "$rc"
if [ $rc -eq 10 ]; then log "pin refused before any write: nothing to restore"; PINNED=0; finish
  echo '{"status":"pin_refused"}' > "$S/end.json"; exit 2; fi
if [ $rc -ne 0 ]; then log "pin failed rc=$rc: restoring, stopping"; finish; echo '{"status":"pin_failed"}' > "$S/end.json"; exit 2; fi
touch "$S/pinned"

# ---- 2. the pinned smoke: proves 600 MHz -----------------------------------------------------------------------------
hl e118 900 anchor_pi,lq_h8 --smoke; rc=$?   # block.sh's smoke: 2 s runs, no approach (EXPN e118-smoke)
h=$(clock_hist "$D/e118-smoke/p900"); step smoke "$rc" "$h"
log "pinned smoke rc=$rc clocks $h"
if ! only600 "$h"; then log "the pin did not hold 600 MHz in every smoke sample: $h"; finish
  echo "{\"status\":\"pin_not_600\",\"clocks\":$h}" > "$S/end.json"; exit 3; fi
[ $rc -eq 0 ] || { log "smoke failed"; finish; echo '{"status":"smoke_failed"}' > "$S/end.json"; exit 3; }

# ---- 3. the launch-reading probe (README: 57 C after 58 C, E60's card-0 gate; else 55/56; else 53/54) ----------------
GATE=
for g in 57:58 55:56 53:54; do
  [ -e "$S/STOP" ] && break
  t=${g%:*}; p=${g#*:}
  pn=$(( 950 + ${t} ))
  hl e118probe "$pn" anchor_pi HL_TARGET="$t" HL_PREHEAT="$p" HL_BURNIN=0; rc=$?
  if [ $rc -eq 0 ] && reached "$D/e118probe/p$pn"; then GATE=$g; step probe 0 "$g reached"; break; fi
  step probe "$rc" "$g not reached"
done
if [ -z "$GATE" ]; then log "no launch reading reachable at 600 MHz (or STOP): no measured passes"; restore_now; finish
  echo '{"status":"gate_unreachable"}' > "$S/end.json"; exit 4; fi
TGT=${GATE%:*}; PRE=${GATE#*:}
log "600 MHz launch gate: $TGT C after $PRE C"

# ---- 4. the 600 MHz passes ---------------------------------------------------------------------------------------
RESERVE=480; est=330; n=0; items=$ITEMS600
for p in 1 2 3 4 5; do
  [ -e "$S/STOP" ] && { log "STOP before p$p: $(cat "$S/STOP")"; break; }
  if [ $(( $(left) - RESERVE - est )) -lt 0 ]; then
    if [ $n -lt 3 ] && [ "$items" = "$ITEMS600" ]; then items=$CUT1; log "cut order applied before p$p (lb_h16, lb_h12, anchor_zeros out)"; est=$(( est * 85 / 100 )); fi
    [ $(( $(left) - RESERVE - est )) -lt 0 ] && { log "no time for p$p ($(left) s left, est $est s)"; break; }
  fi
  t0=$(date +%s)
  hl e118 "$p" "$items" HL_TARGET="$TGT" HL_PREHEAT="$PRE"; rc=$?
  est=$(( $(date +%s) - t0 + 15 ))
  h=$(clock_hist "$D/e118/p$p"); step "pass600_$p" "$rc" "$h"
  log "p$p rc=$rc in $((est - 15)) s, clocks $h"
  [ $rc -eq 0 ] || { log "p$p failed: no more 600 MHz passes"; break; }
  n=$((n + 1))
  sleep 15
done
log "600 MHz passes done: $n"

# ---- 5. ring dump after the pinned passes, then the restore ----------------------------------------------------------
python3 -I $K/gov_e118.py ring --out "$S" --tag after-pinned >> "$S/session.log" 2>&1; step ring_after_pinned $?
restore_now; rc=$?
if [ $rc -ne 0 ]; then log "RESTORE FAILED: stop; keep the claim; the watchdog keeps trying"; finish
  echo '{"status":"restore_failed"}' > "$S/end.json"; exit 5; fi
python3 -I $K/gov_e118.py readback --out "$S" --tag after-restore >> "$S/session.log" 2>&1; step readback_after_restore $?
if [ -e "$S/STOP" ]; then log "envelope STOP: no further launches"; finish; echo '{"status":"envelope_stop"}' > "$S/end.json"; exit 6; fi

# ---- 6. the return burst: normal stepping after the restore ----------------------------------------------------------
hl e118back 901 anchor_pi,lq_h8 --smoke E118_HEATER=$K/heater_pi.sh; rc=$?
h=$(clock_hist "$D/e118back-smoke/p901"); step back "$rc" "$h"; log "return burst rc=$rc clocks $h"
python3 -I $K/gov_e118.py ring --out "$S" --tag after-back >> "$S/session.log" 2>&1; step ring_after_back $?

# ---- 7. the 800 MHz control ----------------------------------------------------------------------------------------
TC=57; PC=58; estc=150; nc=0; pc=1
while [ $pc -le 6 ] && [ $nc -lt 3 ]; do
  [ -e "$S/STOP" ] && { log "STOP before control pass $pc"; break; }
  [ $(( $(left) - 150 - estc )) -lt 0 ] && { log "no time for control pass $pc ($(left) s left)"; break; }
  t0=$(date +%s)
  hl e118c "$pc" "$ITEMSC" HL_TARGET="$TC" HL_PREHEAT="$PC" E118_HEATER=$K/heater_pi.sh; rc=$?
  estc=$(( $(date +%s) - t0 + 10 ))
  h=$(clock_hist "$D/e118c/p$pc"); step "control_$pc" "$rc" "$h gate $TC/$PC"; log "control p$pc rc=$rc clocks $h gate $TC/$PC"
  if [ $rc -eq 0 ]; then nc=$((nc + 1))
  elif [ $rc -eq 1 ] && grep -q 'three runs in a row' "$D/e118c/p$pc/run.log" 2>/dev/null && [ $TC = 57 ]; then
    TC=55; PC=56; log "control gate unreachable at 57/58: 55/56 from the next pass"
  else break; fi
  pc=$((pc + 1)); sleep 10
done
log "control passes done: $nc"

# ---- 8. closing reads ----------------------------------------------------------------------------------------------
python3 -I $K/gov_e118.py readback --out "$S" --tag closing >> "$S/session.log" 2>&1; step readback_closing $?
finish
echo "{\"status\":\"done\",\"passes600\":$n,\"control\":$nc,\"gate600\":\"$TGT/$PRE\",\"t_ms\":$(date +%s%3N)}" > "$S/end.json"
log "session done"
