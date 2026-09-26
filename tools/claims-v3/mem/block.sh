#!/usr/bin/env bash
# V3-MEM, one pass on the local card (PLAN3.md section 2 "V3-MEM"; new code N1). See README.md next to this file.
#
#   bash tools/claims-v3/mem/block.sh <pass> [--smoke]          # from the tree root (aifoundry2: this repo; aifoundry3
#                                                               # and aifoundry1: ~/nekko; aifoundry1: V3_DEVICE=0 or 1)
#   V3_DRY=1 bash tools/claims-v3/mem/block.sh <pass>           # no device access: prints every device call
#
# A pass: [busy-rule cards] the idle state (ettelem config); arena base (--info); the op lists generated off-card
# (seeds 100+k, 200+k, 20+k); [governor-free cards] heat to 76 C; the 10 Hz sampler; the 11 programs t_raw t_glitch
# t_rawodd ladder decomp l3map msmap bits refresh refresh_jit pagetimeout in shuf order, each its own process; ladder +
# decomp from requesters 7, 24, 31 (--hart 64*S); the sampler stopped (SIGTERM); then, in passes 1-3 (or a later pass
# while fewer than 3 wake-up probes are kept on this card): [governor-free cards] heat top-up to 76 C, a 1 s sample, the
# wake-up probe, a 1 s sample; [busy-rule cards] the idle state again. Every device process is under timeout 10 (hold10)
# and memprobe's --budget 8. Passes > 5 are conditional re-runs: they do nothing when the card already has 5 kept
# passes and 3 kept wake-up probes.
# Cards (lib.sh): GOV_FREE (heat to 76 C first) on every card but aifoundry3. The clock rule (memv3.py clock_rule):
# aifoundry2 keeps its registered rule (any sample, and the probe's pre/post samples, off 600 MHz drop); aifoundry3 is
# pinned (clock recorded); every other card (aifoundry1's two) has the busy rule: only clock readings taken inside a
# memprobe kernel, and the probe's own clock, can drop; idle brackets are recorded, never a drop. On busy-rule cards
# each heat (before the X1 part, before the probe) makes at least one heater launch, so a card idling in a low-power
# state (aifoundry1-c0: 300 MHz) is at 600 MHz when the kernels start.
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"      # cd's to the tree root; CARD, MEMPROBE, HEATER, DATA_ROOT, helpers
K=${1:?usage: block.sh <pass> [--smoke]}
case "$K" in ''|*[!0-9]*|0) echo "pass must be a positive integer" >&2; exit 2 ;; esac
MODE=full; [ "${2:-}" = --smoke ] && MODE=smoke
MEM=tools/claims-v3/mem
PY="python3 $MEM/memv3.py"
G="python3 workloads/memprobe/gen_ops.py"
KELF=$(dirname "$MEMPROBE")/../kernel/memprobe.elf

RULE=$($PY rule --card "$CARD")
case "$RULE" in registered|pinned|busy) ;; *) log "memv3.py rule gave '$RULE' for $CARD: not starting"; exit 2 ;; esac
# lib.sh's GOV_FREE and memv3.py's rule must name the same pinned card
if { [ -z "$GOV_FREE" ] && [ "$RULE" != pinned ]; } || { [ -n "$GOV_FREE" ] && [ "$RULE" = pinned ]; }; then
  log "lib.sh GOV_FREE='$GOV_FREE' and memv3.py rule '$RULE' disagree for $CARD: not starting"; exit 2
fi

others_present && exit 3
ours_running && { log "a device process of ours is still running, not starting"; exit 3; }
# The module's use count catches a holder that ps does not name (plan 2.13: 0, or 1 while only our sampler runs). It
# counts every card the module drives: on a host with several cards (V3_DEVICE set, aifoundry1) the other card's
# queue holds its own card, so the check is skipped there and ours_running (per card) and others_present (other
# users, their device processes and a running CI job) decide.
if [ -z "${V3_DRY:-}" ] && [ -z "${V3_DEVICE:-}" ]; then
  u=$(lsmod 2>/dev/null | awk '$1=="et_soc1"{print $3}')
  if [ -n "$u" ] && [ "$u" != 0 ]; then log "et_soc1 use count $u: the card is held, not starting"; exit 3; fi
fi

# The op lists must be the pre-registered generator's (the reducer's prereg/mp/gen_ops.py): on aifoundry3 and
# aifoundry1 the tree is a synced copy, and an older gen_ops.py would give other programs under the same names.
if ! cmp -s workloads/memprobe/gen_ops.py "$MEM/prereg/mp/gen_ops.py"; then
  log "workloads/memprobe/gen_ops.py differs from $MEM/prereg/mp/gen_ops.py (sync it): not starting"; exit 2
fi

X1=1   # a pass > 5 runs the X1/X2/timer programs only while the card has fewer than 5 kept passes
if [ "$MODE" = full ] && [ "$K" -gt 5 ]; then
  read -r NX NW < <($PY kept --root "$DATA_ROOT/mem" --card "$CARD")
  if [ "${NX:-0}" -ge 5 ] && [ "${NW:-0}" -ge 3 ]; then
    log "mem p$K not needed: $NX kept passes, $NW kept wake-up probes"; exit 0
  fi
  [ "${NX:-0}" -ge 5 ] && X1=0
fi
WAKE=0
if [ "$MODE" = full ]; then WAKE=$($PY wake-needed --root "$DATA_ROOT/mem" --card "$CARD" --pass "$K"); fi
if [ "$X1" = 0 ] && [ "$WAKE" != 1 ]; then   # nothing to run: do not open the card for --info alone
  log "mem p$K not needed: ${NX:-?} kept passes; the wake-up probes still pending are covered by passes 1-3"; exit 0
fi

# lib.sh's heat_to 76 with an others_present check before each heater launch (lib's loop has none, and heating can
# take up to 150 launches). Returns 0 at >= 76 C, 1 if it gave up, 3 if another user arrived. Governor-free cards only
# (aifoundry2 and aifoundry1's two: TDP 65 W, threshold 65 C; aifoundry3 is pinned and needs no heater).
# Like lib's heat_to it never heats blind: a die read that fails launches nothing, and 4 failed reads in a row give up
# (no drain here: on aifoundry1 dev_mngt_service opens both cards; the next block's start_sampler drains).
# Busy-rule cards (aifoundry1's two) get at least one heater launch per call even on a die already at 76 C: card 0
# idles in "low_power" at 300 MHz and reached 600 MHz only at the end of its first 2 s launch (25 Sep clock test), so
# one launch puts the card at its working point before the 2-85 ms memprobe kernels (amendment, before any data).
heat76() {
  local out=$1 t i empty=0 n=0
  [ -n "$GOV_FREE" ] || return 0
  if [ -n "${V3_DRY:-}" ]; then
    heat_to 76 "$out"
    [ "$RULE" = busy ] && echo "DRY (busy-rule card: at least one launch) hold10: $HEATER --test fma --type fp32" \
      "--pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1" >&2
    return 0
  fi
  for i in $(seq 1 150); do
    t=$(die_c); echo "{\"t_ms\":$(now_ms),\"die_c\":${t:-0}}" >> "$out"
    if [ -z "$t" ]; then
      empty=$((empty + 1))
      [ $empty -ge 4 ] && { log "heat76: no die temperature in 4 reads; not heating blind"; return 1; }
      sleep 2; continue
    fi
    empty=0
    if [ "$t" -ge 76 ] && { [ "$RULE" != busy ] || [ $n -ge 1 ]; }; then return 0; fi
    others_present && return 3
    hold10 "$HEATER" --test fma --type fp32 --pattern none --values randn \
      --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1 > /dev/null 2>&1
    n=$((n + 1))
  done
  log "heat76: gave up at ${t:-?} C"; return 1
}

# The card's state between kernels, busy-rule cards only (the registered cards keep the registered procedure; their idle
# clock is in the sampler's between-kernel readings): `ettelem config` (power state, minion clock and voltage), a
# management read made while no kernel and no sampler runs, into idle_state.jsonl. aifoundry1's card 0 idles in
# "low_power" at 300 MHz, card 1 in "managed_power" at 600 MHz. Recorded, never a drop rule.
idle_state() {
  [ "$RULE" = busy ] || return 0
  local l
  if [ -n "${V3_DRY:-}" ]; then
    echo "DRY ettelem config ($1)" >&2; l='{"dry":true}'
  else
    l=$(timeout 10 "$ETTELEM" config 2>/dev/null < /dev/null | grep '^{' | tail -1)
    python3 -c 'import json,sys; json.loads(sys.argv[1])' "$l" 2>/dev/null || l=null
  fi
  echo "{\"t_ms\":$(now_ms),\"at\":\"$1\",\"config\":$l}" >> "$OUT/idle_state.jsonl"
}

EXPN=mem; [ "$MODE" = smoke ] && EXPN=mem-smoke
if [ -n "${V3_FORCE:-}" ] && [ -d "$DATA_ROOT/$EXPN/p$K" ]; then   # a forced re-run never mixes with the old files
  mv "$DATA_ROOT/$EXPN/p$K" "$DATA_ROOT/$EXPN/p$K.attempt-$(date +%s)"
fi
block_begin "$EXPN" "$K"
[ "$X1" = 0 ] && log "p$K: this card already has 5 kept passes; wake-up probe only"
find "$MEM" -type f \( -name '*.py' -o -name '*.sh' -o -name '*.md' \) | sort | xargs sha256sum >> "$OUT/code.sha256" 2>/dev/null
sha256sum workloads/memprobe/gen_ops.py >> "$OUT/code.sha256" 2>/dev/null
[ -z "${V3_DRY:-}" ] && sha256sum "$MEMPROBE" "$KELF" > "$OUT/binary.sha256" 2>/dev/null
if [ -z "${V3_DRY:-}" ] && { [ ! -x "$MEMPROBE" ] || [ ! -f "$KELF" ]; }; then
  block_end fail "no memprobe build at $MEMPROBE"; exit 1
fi
idle_state start

# One memprobe process: run_prog <out-dir> <ops> [host args...]; results into <out-dir>/<name>.u32, MEMPROBE lines into
# memprobe.log, each process's rc and wall time into runs.jsonl.
NFAIL=0; CORE=1   # a failed core program (the 11 X1 programs) fails the block; req/wake failures are only noted
run_prog() {
  local dir=$1 ops=$2; shift 2
  local name t0 rc; name=$(basename "$ops" .ops); t0=$(now_ms)
  if others_present; then   # someone arrived mid-pass: leave the card to them; the queue retries the pass (rc 3)
    stop_sampler; block_end fail "another user arrived before ${dir#"$OUT"}/$name"; exit 3
  fi
  echo "# $(date +%T) ${dir#"$OUT"}/$name $*" >> "$OUT/memprobe.err"
  if [ -n "${V3_DRY:-}" ]; then
    hold10 "$MEMPROBE" "$@" --program "$ops" --out-dir "$dir" --budget 8 >> "$OUT/memprobe.log"
  else
    hold10 "$MEMPROBE" "$@" --program "$ops" --out-dir "$dir" --budget 8 >> "$OUT/memprobe.log" 2>> "$OUT/memprobe.err"
  fi
  rc=$?
  [ $rc -ne 0 ] && [ "$CORE" = 1 ] && NFAIL=$((NFAIL + 1))
  echo "{\"name\":\"$name\",\"dir\":\"${dir#"$OUT"}\",\"args\":\"$*\",\"rc\":$rc,\"t0_ms\":$t0,\"t1_ms\":$(now_ms)}" >> "$OUT/runs.jsonl"
  return $rc
}
gen() { "$@" >> "$OUT/gen.log" 2>&1 || { block_end fail "op generation failed: ${*: -4}"; exit 1; }; }
# 1 s of 5 Hz samples (plan: ettelem sample --seconds 1 --every-ms 200), through start_sampler for its retry + drain.
sample1s() { start_sampler "$1" 1 --every-ms 200 && { sleep 1.2; stop_sampler; }; }
# rawodd: 4,000 (stamp, raw pair) ops so raw reads also land on odd low bits (the plan's command, verbatim).
gen_rawodd() {
  python3 -c "import sys; sys.path.insert(0,'workloads/memprobe'); import gen_ops as g; p=g.Prog(); [(p.stamp(('s',i)), p.raw(('raw',i))) for i in range(4000)]; p.write('$1','t_rawodd',{})"
}

# ---- arena base (bits needs it; P10 checks it is 1 GB aligned)
hold10 "$MEMPROBE" --info > "$OUT/info.log" 2>&1
[ -n "${V3_DRY:-}" ] && cat "$OUT/info.log" >&2
BASE=$(grep -o '"arena_base":"0x[0-9a-f]*"' "$OUT/info.log" | grep -o '0x[0-9a-f]*' | head -1)
if [ -z "$BASE" ] && [ -n "${V3_DRY:-}" ]; then BASE=0x8040000000; log "DRY: arena base taken as $BASE"; fi
if [ -z "$BASE" ] || ! python3 -c "import sys; sys.exit(int('$BASE', 16) % (1 << 30) != 0)"; then
  block_end fail "arena base '${BASE}' missing or not 1 GB aligned"; exit 1
fi
log "arena base $BASE"

if [ "$MODE" = smoke ]; then
  # ---- smoke: every component once, in its smallest form (about 25 s of card time)
  gen $G timer --out "$OUT"
  gen gen_rawodd "$OUT"
  gen $G ladder --out "$OUT/req7" --lines 4 --seed 1
  gen $G decomp --out "$OUT/req7" --lines 16 --reps 1 --pre-delay 1000 --seed 200
  gen $G wakeup --out "$OUT/wake" --reps 1 --seed 20 --delays 0,1000
  if [ -n "$GOV_FREE" ]; then   # one heater launch (the heat_to command) instead of a full heat
    t=$(die_c); echo "{\"t_ms\":$(now_ms),\"die_c\":${t:-null}}" >> "$OUT/heat.jsonl"
    hold10 "$HEATER" --test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 \
      --seconds 2 --seed 1 > "$OUT/heater.log" 2>&1; echo "heater rc $?" >> "$OUT/heater.log"
    [ -n "${V3_DRY:-}" ] && cat "$OUT/heater.log" >&2
    t=$(die_c); echo "{\"t_ms\":$(now_ms),\"die_c\":${t:-null}}" >> "$OUT/heat.jsonl"
  fi
  start_sampler "$OUT/telemetry.jsonl" 60 || log "sampler did not start"
  run_prog "$OUT" "$OUT/t_raw.ops"
  run_prog "$OUT" "$OUT/t_rawodd.ops"
  run_prog "$OUT/req7" "$OUT/req7/ladder.ops" --hart 448
  run_prog "$OUT/req7" "$OUT/req7/decomp.ops" --hart 448
  run_prog "$OUT" "$OUT/t_glitch.ops"
  stop_sampler
  sample1s "$OUT/wake/pre.jsonl"
  run_prog "$OUT/wake" "$OUT/wake/wakeup.ops"
  sample1s "$OUT/wake/post.jsonl"
  idle_state end
  rm -f "$OUT"/*.ops "$OUT"/*/*.ops
  $PY smoke --out "$OUT" --card "$CARD" > "$OUT/smoke.json" 2>&1
  cat "$OUT/smoke.json"
  if [ -n "${V3_DRY:-}" ]; then block_end ok "dry run"; exit 0; fi
  if grep -q '"ok": true' "$OUT/smoke.json"; then block_end ok "smoke ok"; exit 0; fi
  block_end fail "smoke problems: $(python3 -c "import json;print('; '.join(json.load(open('$OUT/smoke.json')).get('problems',[])))" 2>/dev/null | tr -d '"\\')"
  exit 1
fi

# ---- full pass: op lists off-card first (the plan's commands; seeds 100+k, 200+k, 20+k)
s=$((100 + K))
if [ "$X1" = 1 ]; then
gen $G timer --out "$OUT"
gen $G ladder --out "$OUT" --lines 64 --seed 1
gen $G decomp --out "$OUT" --lines 1500 --reps 3 --pre-delay 1000 --seed $s
gen $G l3map --out "$OUT" --lines 8192
gen $G msmap --out "$OUT" --lines 64 --seed $s
gen $G bits --out "$OUT" --base "$BASE" --trials 150 --seed $s
gen $G refresh --out "$OUT" --name refresh_jit --n 19000 --jitter 3000 --start 0x1000 --seed $s
gen $G refresh --out "$OUT" --n 24000 --start 0x1000
gen $G pagetimeout --out "$OUT" --row-bit 13 --trials 60 --delays 0,100,200,400,700,1000,1500,2000,3000,5000,8000,12000,20000 --seed $s
gen gen_rawodd "$OUT"
for S in 7 24 31; do
  gen $G ladder --out "$OUT/req$S" --lines 64 --seed 1
  gen $G decomp --out "$OUT/req$S" --lines 1500 --reps 3 --pre-delay 1000 --seed $((200 + K))
done
fi
[ "$WAKE" = 1 ] && gen $G wakeup --out "$OUT/wake" --reps 20 --seed $((20 + K)) \
  --delays 0,100,300,1000,10000,100000,1000000,4000000,8000000,16000000

# ---- card part
if [ "$X1" = 1 ]; then
if [ -n "$GOV_FREE" ]; then
  heat76 "$OUT/heat.jsonl"; rc=$?
  [ $rc = 3 ] && { block_end fail "another user arrived during heating"; exit 3; }
  [ $rc != 0 ] && { block_end fail "heat to 76 C gave up"; exit 1; }
fi
if ! start_sampler "$OUT/telemetry.jsonl" 400; then
  # a governor-free card drops an X1 part without a clock reading (registered and busy rules), so do not spend the card
  # on it; the pinned card (aifoundry3) does not drop on the clock
  [ -n "$GOV_FREE" ] && { block_end fail "sampler did not start"; exit 1; }
  log "sampler did not start; the pinned card continues (its clock is recorded, not a drop rule)"
fi
ORDER=$(shuf -e t_raw t_glitch t_rawodd ladder decomp l3map msmap bits refresh refresh_jit pagetimeout | tr '\n' ' ')
echo "$ORDER" > "$OUT/order.txt"
for p in $ORDER; do run_prog "$OUT" "$OUT/$p.ops"; done
CORE=0
for S in 7 24 31; do
  for p in ladder decomp; do run_prog "$OUT/req$S" "$OUT/req$S/$p.ops" --hart $((64 * S)); done
done
stop_sampler
fi

if [ "$WAKE" = 1 ]; then
  W=$OUT/wake
  # Someone arrived after the X1 part: skip only the probe (a later pass re-runs it while fewer than 3 are kept), so
  # the finished X1 part is not thrown away with an exit 3.
  hrc=0
  if others_present; then hrc=3; else [ -n "$GOV_FREE" ] && { heat76 "$W/heat.jsonl"; hrc=$?; }; fi
  if [ $hrc = 3 ]; then
    log "another user arrived: wake-up probe skipped"; echo "another user arrived" > "$W/skipped"
  else
    [ $hrc = 1 ] && log "heat to 76 C before the probe gave up (the pre sample records the clock)"
    # The registered rule (aifoundry2) drops a probe without a pre-probe clock reading, so it does not spend the card
    # on one. On the other cards the pre and post samples are recorded (on a busy-rule card they are idle brackets;
    # the probe is judged on its own clock), so the probe runs anyway.
    if sample1s "$W/pre.jsonl" || [ "$RULE" != registered ]; then
      run_prog "$W" "$W/wakeup.ops"
      sample1s "$W/post.jsonl"
    else
      log "no pre-probe sample: probe skipped"
    fi
  fi
  now_ms > "$W/t_end"
fi

idle_state end

# ---- checks, drop rules (recorded; the reducer re-derives them from these files), cleanup
$PY finish --out "$OUT" --card "$CARD" > "$OUT/drop.json" 2> "$OUT/finish.err"
rm -f "$OUT"/*.ops "$OUT"/req*/*.ops "$OUT"/wake/*.ops                 # regenerable from the seeds
for f in "$OUT"/*.json "$OUT"/req*/*.json "$OUT"/wake/wakeup.json; do  # gen_ops labels only
  case "$(basename "$f")" in drop.json|block.json) ;; *) [ -f "$f" ] && gzip -f "$f" ;; esac
done
[ -f "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
NOTE=$(python3 - "$OUT/drop.json" "$WAKE" "$X1" "$OUT/wake/skipped" <<'EOF' 2>/dev/null
import json, os, sys
d = json.load(open(sys.argv[1])); w = d.get("wake")
x1 = "x1 keep" if d["x1_keep"] else "x1 DROP (%s)" % d["x1_reason"][:120]
if sys.argv[3] == "0": x1 = "no x1 (wake-up probe only)"
wk = "no probe" if sys.argv[2] != "1" else ("probe keep" if w and w["keep"] else "probe DROP (%s)" % ((w or {}).get("reason") or "missing"))
if sys.argv[2] == "1" and os.path.exists(sys.argv[4]): wk = "probe skipped (another user arrived)"
pf = d.get("program_failures") or []
extra = ""
if str(d.get("clock_rule", "")).startswith("busy"):   # busy-rule cards: the clocks read inside and between kernels
    sp = d.get("clock_split") or {}
    fmt = lambda c: ",".join("%s x%d" % kv for kv in sorted((c or {}).get("mhz_minion", {}).items())) or "none"
    extra = "; busy %s, idle %s MHz" % (fmt(sp.get("busy")), fmt(sp.get("idle")))
    if w and w.get("probe_mhz_eff"): extra += "; probe %.1f MHz" % w["probe_mhz_eff"]
print(("%s; %s; %d program failures%s" % (x1, wk, len(pf), extra)).replace('"', "").replace("\\", ""))
EOF
)
if [ -n "${V3_DRY:-}" ]; then block_end ok "dry run"; exit 0; fi
if [ "$NFAIL" -gt 0 ]; then block_end fail "${NOTE:-$NFAIL program failures}"; exit 1; fi
block_end ok "${NOTE:-checks did not run}"
