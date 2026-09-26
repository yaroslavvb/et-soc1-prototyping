#!/usr/bin/env bash
# V3-CAT (PLAN3 section 2, "Energy catalogue: a within-card temperature panel and the DRAM-row rows on aifoundry3"):
# one pass of the energy catalogue on the local card, as one block.
#
#   bash tools/claims-v3/cat/block.sh <pass> [--smoke]
#   V3_DEVICE=<0|1> bash tools/claims-v3/cat/block.sh <pass>   # aifoundry1: card 0 or 1 (lib.sh: ET_DEVICES)
#   V3_DRY=1 bash tools/claims-v3/cat/block.sh <pass>          # print every device call, touch nothing
#   CAT_HOLD_C=<C> ...                                          # pinned card's hot passes: override the hold temperature
#
# Cards: governor-free (lib.sh GOV_FREE: aifoundry2, aifoundry1-c0, aifoundry1-c1: heat before power work, drop
# busy samples off 600 MHz) run aifoundry2's registered design; the pinned card (aifoundry3) its own. The pass number
# fixes the arm and condition (the registered order, arm A and arm B alternating on each card):
#   governor-free (11 blocks): 1 A-W  2 B  3 A-H  4 A-W  5 B  6 A-H  7 A-W  8 B  9 A-H  10 A-W  11 A-H
#   pinned        (12 blocks): 1 A-C  2 B  3 A-H  4 B  5 A-C  6 B  7 A-H  8 B  9 A-C  10 B  11 A-H  12 B
# Arm A = the 30-configuration temperature panel, --burst 3 --gap 4.5 --seed 20<k> (k = the arm-A pass index);
#   W = warm, governor-free cards (no hold: wait until <= 82 C, then heat_to 76), H = hold hot (governor-free
#   --hold-hot 88, pinned --hold-hot Tmax-1 from V3-IDLE), C = cool, pinned card (no hold, no heater).
# Arm B = dramrow2, tload/dram, tstore/dram, l1fill/stride32, l1fill/stride64, tload/scp, fence, nop (23
#   configurations), run_catalogue's default --burst 3 --gap 5, --seed 30<k>; governor-free cards preheated to 76 C.
# Data: $DATA_ROOT/cat/p<pass>/ (runs, telemetry, marks gzipped at the end; pass.json, configs.json, check.json,
# config_start.json: the card's power state, clock and voltage before the block touches it).
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
others_present && exit 3
# the runner's own others_present check sources lib.sh again: on aifoundry1 it needs V3_DEVICE in its environment
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block.sh <pass> [--smoke]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/cat                       # lib.sh has cd'd to the tree root
RUNNER=$HERE/run_catalogue_t10.py
HOST_BIN=$ENERCAT2                             # build/enercat_v2/host/enercat_host (dramrow2 needs --jump-every)

PANEL="fnmadd.ps/random,fmadd.ps/random/h2,flog.ps/random,fmul.pi/random,fmul.ps/random,frcp.ps/random,fsub.ps/random,fadd.ps/random,fexp.ps/random/h2,feq.ps/random,wire/hop2/random,wire/hop4/random,wire/hop6/random,fmadd.s/random,fmul.s/random,fcvt.s.w/random,fround.ps/random,fmadd.ps/zeros,fmul.s/zeros,fadd.s/random,fadd.s/zeros,fsw.ps/random,tstore/dram/random,tload/scp/random,tstore/scp/random,tload/dram/random,st_stream/dram/random,fxor.pi/random,fadd.pi/random,fsgnj.ps/random"
ARMB="dramrow2,tload/dram,tstore/dram,l1fill/stride32,l1fill/stride64,tload/scp,fence,nop"
SMOKE_ONLY="fmul.ps/random,tload/scp/random,dramrow2/seq/random"   # one compute, one prefill, one jump-flag config
# Per-card parameters. Governor-free cards: aifoundry2's registered values (hold 88 C, warm passes start <= 82 C,
# heat_to 76 C first); aifoundry1's two cards take them unchanged (same 65 C / 65 W governor thresholds, same TDP;
# README "Four cards"). The pinned card: Tmax - 1 (hold_target below), no heat_to, cool passes.
GF_HOLD=88; GF_WARM_MAX=82; GF_HEAT_TO=76; PREHEAT_MAX_LAUNCHES=40

if [ -n "$GOV_FREE" ]; then
  TABLE="1:A:W:1 2:B:-:1 3:A:H:2 4:A:W:3 5:B:-:2 6:A:H:4 7:A:W:5 8:B:-:3 9:A:H:6 10:A:W:7 11:A:H:8"
else
  TABLE="1:A:C:1 2:B:-:1 3:A:H:2 4:B:-:2 5:A:C:3 6:B:-:3 7:A:H:4 8:B:-:4 9:A:C:5 10:B:-:5 11:A:H:6 12:B:-:6"
fi
if [ -n "$SMOKE" ]; then
  ARM=S; COND=H; K=0; SEED=1; ONLY=$SMOKE_ONLY; TIMING="--burst 1 --gap 4.5 --lead 3"; EXPN=cat-smoke
else
  ent=$(printf '%s\n' $TABLE | grep "^$PASS:" || true)
  [ -n "$ent" ] || { echo "no pass $PASS on $CARD (table: $TABLE)" >&2; exit 2; }
  IFS=: read -r _ ARM COND K <<< "$ent"
  EXPN=cat
  if [ "$ARM" = A ]; then ONLY=$PANEL; SEED=20$K; TIMING="--burst 3 --gap 4.5"
  else ONLY=$ARMB; SEED=30$K; TIMING=""; fi       # arm B: run_catalogue's defaults (--burst 3 --gap 5)
fi

# ---- preflight: files only, no device ------------------------------------------------------------------------
need_jump=; [ "$ARM" = B ] || [ "$ARM" = S ] && need_jump=1
need_heater=; [ "$COND" = H ] && need_heater=1
pf=()
[ -x "$HOST_BIN" ] || pf+=("missing $HOST_BIN")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -n "$need_heater" ] && [ ! -x "$HEATER" ] && pf+=("missing heater $HEATER")
if [ -x "$HOST_BIN" ]; then
  [ -n "$need_jump" ] && ! grep -a -q -- '--jump-every' "$HOST_BIN" && pf+=("$HOST_BIN has no --jump-every (dramrow2)")
  kelf=$(grep -a -o '/[[:alnum:]/._-]*/enercat\.elf' "$HOST_BIN" | head -1)
  [ -n "$kelf" ] && [ ! -f "$kelf" ] && pf+=("kernel $kelf (compiled into $HOST_BIN) not found")
fi
if [ -n "$need_heater" ] && [ -x "$HEATER" ]; then
  grep -a -q -- '--per-shire' "$HEATER" && grep -a -q 'randn' "$HEATER" || pf+=("$HEATER lacks --per-shire/randn")
fi
LIST=$(python3 "$RUNNER" /dev/null --root "$V3_ROOT" --only "$ONLY" --passes 1 $TIMING --seed "$SEED" --host-bin "$HOST_BIN" \
       ${need_heater:+--hold-hot 0} --list 2>&1) || pf+=("runner --list: $LIST")
python3 -c 'import numpy' 2>/dev/null || pf+=("python3 has no numpy (post-pass check)")
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi
NCFG=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["n"])' "$LIST")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST")

# ---- the hold temperature for a hot pass -----------------------------------------------------------------------
# Governor-free cards: 88 C. Pinned card (aifoundry3): Tmax - 1, Tmax = the highest minshire in V3-IDLE's telemetry on this card
# ($DATA_ROOT/idle/p<N>/telemetry.jsonl.gz, tools/claims-v3/idle/block.sh); fixed at
# the first hot pass in $DATA_ROOT/cat/hold_c.json so every hot pass holds the same temperature. CAT_HOLD_C overrides.
hold_target() {
  if [ -n "$GOV_FREE" ]; then echo "$GF_HOLD"; return 0; fi
  if [ -n "${CAT_HOLD_C:-}" ]; then echo "$CAT_HOLD_C"; return 0; fi
  local f=$DATA_ROOT/cat/hold_c.json
  if [ ! -f "$f" ]; then
    python3 - "$DATA_ROOT" "$f" <<'EOF' || return 1
import glob, gzip, json, os, sys
root, out = sys.argv[1], sys.argv[2]
files = [p for p in glob.glob(os.path.join(root, "idle", "p*", "telemetry.jsonl*"))
         if os.path.basename(os.path.dirname(p))[1:].isdigit()]   # V3-IDLE passes; not idle-smoke, not .attempt-*
tmax, src = None, None
for p in files:
    op = gzip.open if p.endswith(".gz") else open
    try:
        for line in op(p, "rt"):
            if '"minshire"' not in line:
                continue
            try:
                t = json.loads(line)["temp_c"]["minshire"][0]
            except Exception:
                continue
            if tmax is None or t > tmax:
                tmax, src = t, p
    except OSError:
        pass
if tmax is None:
    sys.exit(1)
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"tmax_c": tmax, "hold_c": tmax - 1, "source": src, "files": len(files)}, open(out, "w"))
EOF
  fi
  python3 -c 'import json,sys; print(int(json.load(open(sys.argv[1]))["hold_c"]))' "$f"
}
HOLD=
if [ -n "$need_heater" ]; then
  if [ -n "$SMOKE" ]; then HOLD=200    # one heater launch through the hold path, never reached
  else HOLD=$(hold_target) || { echo "$CARD (pinned) hot pass: no V3-IDLE telemetry under $DATA_ROOT/idle/p*/ and no CAT_HOLD_C" >&2; exit 2; }
  fi
fi

# ---- local helpers (lib.sh's heat_to is governor-free cards only, with a fixed 150-launch loop) ---------------------
HEAT_ARGS=(--test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1)
# block_end prints die_c's output unquoted ("die_c_end":, when ettelem does not start); lib_die_c is lib's (or lib's
# dry) die_c, and finish() gives block_end a die_c that prints null instead, and none at all after an intrusion.
eval "lib_die_c() $(declare -f die_c | tail -n +2)"
finish() {  # finish <status> <note>
  if [ "$1" = others ]; then die_c() { echo null; }; else die_c() { local t; t=$(lib_die_c); echo "${t:-null}"; }; fi
  block_end "$1" "$2"
}
# Another user logged in, or another user's device process: stop, never open the card again, exit 3 (the queue's
# "someone else on the card": it moves this attempt aside and retries after a wait).
gz_out() { local f; for f in telemetry.jsonl runs.jsonl marks.jsonl; do [ -s "$OUT/$f" ] && gzip -f "$OUT/$f"; done; return 0; }
yield_exit() { stop_sampler; gz_out; finish others "$1"; exit 3; }
# cat_heat_to <target C> <max launches> <log>: die_c then a 2 s heater launch until the die reads >= target; both cards.
cat_heat_to() {
  local target=$1 max=$2 out=$3 t= i
  if [ -n "${V3_DRY:-}" ]; then echo "DRY cat_heat_to $target (<= $max x hold10 $HEATER ${HEAT_ARGS[*]})" >&2; return 0; fi
  for i in $(seq 0 "$max"); do
    others_present && yield_exit "others present during the preheat"
    t=$(die_c); echo "{\"t_ms\":$(now_ms),\"die_c\":${t:-0},\"target\":$target}" >> "$out"
    [ -n "$t" ] && [ "$t" -ge "$target" ] && return 0
    [ "$i" -ge "$max" ] && break
    hold10 "$HEATER" "${HEAT_ARGS[@]}" > /dev/null 2>&1
  done
  log "cat_heat_to $target: stopped at ${t:-?} C after $max launches"; return 1
}
# wait_cool <max C> <max s> <log>: no launch, a die_c every 20 s until the die reads <= max C.
wait_cool() {
  local lim=$1 secs=$2 out=$3 t= w=0
  if [ -n "${V3_DRY:-}" ]; then echo "DRY wait_cool <= $lim C (die_c every 20 s, <= $secs s)" >&2; return 0; fi
  while :; do
    others_present && yield_exit "others present while waiting for the die to cool"
    t=$(die_c); echo "{\"t_ms\":$(now_ms),\"die_c\":${t:-0},\"wait_le\":$lim}" >> "$out"
    [ -n "$t" ] && [ "$t" -le "$lim" ] && return 0
    [ "$w" -ge "$secs" ] && { log "wait_cool $lim: still ${t:-?} C after $secs s"; return 1; }
    sleep 20; w=$((w + 20))
  done
}

# ---- the block ---------------------------------------------------------------------------------------------------
d=$DATA_ROOT/$EXPN/p$PASS
if [ -d "$d" ] && { [ -n "$SMOKE" ] || [ ! -e "$d/block.json" ] || [ -n "${V3_FORCE:-}" ]; }; then
  mv "$d" "$d.attempt-$(date +%s)"     # never append to an earlier attempt's runs.jsonl
fi
[ -n "$SMOKE" ] && export V3_FORCE=1
block_begin "$EXPN" "$PASS"
[ -n "$SMOKE" ] && sha256sum tools/claims-v3/lib.sh "$HERE"/* > "$OUT/code.sha256" 2>/dev/null
# The card's idle state before this block heats or launches anything: ettelem config (read-only: TDP, temperature
# threshold, power state, minion clock and voltage). aifoundry1's card 0 (firmware 1.4.1) was read in "low_power" at
# 300 MHz / ~400 mV before any launch (and at 600 MHz after launches); the sampler's mhz.minion and die_mv.minion
# give the state of every idle bracket, which catlib.py records per burst (idle_state) and reduce.py reports per card.
card_config() {
  if [ -n "${V3_DRY:-}" ]; then echo "DRY ettelem config" >&2; echo '{"dry":true}'; return 0; fi
  timeout 20 "$ETTELEM" config 2>/dev/null < /dev/null | grep '^{' | tail -1 || true
}
card_config > "$OUT/config_start.json"
python3 - "$OUT/pass.json" "$OUT/config_start.json" <<EOF
import json, sys
try:
    cfg0 = json.load(open(sys.argv[2]))
except ValueError:
    cfg0 = None
json.dump({"exp": "cat", "card": "$CARD", "pass": $PASS, "smoke": bool("$SMOKE"), "arm": "$ARM", "cond": "$COND", "k": $K,
           "seed": $SEED, "hold_c": ${HOLD:-None}, "only": "$ONLY", "timing": "$TIMING", "host_bin": "$HOST_BIN",
           "heater": "$HEATER", "n_cfg": $NCFG, "max_s": $MAXS, "gov_free": bool("$GOV_FREE"),
           "device": "${V3_DEVICE:-}" or None, "config_start": cfg0}, open(sys.argv[1], "w"), indent=1)
EOF
log "$EXPN p$PASS: arm $ARM cond $COND k $K seed $SEED hold ${HOLD:-none}; $NCFG configurations, <= $((MAXS / 60 + 1)) min"

# temperature before the sampler starts (die_c and the heater may open the card only now)
if [ -z "$SMOKE" ]; then
  if [ -n "$GOV_FREE" ]; then
    if [ "$COND" = W ]; then wait_cool "$GF_WARM_MAX" 600 "$OUT/preheat.jsonl" || true; fi
    heat_to "$GF_HEAT_TO" "$OUT/preheat.jsonl" || { finish fail "$CARD did not reach $GF_HEAT_TO C"; exit 1; }
  fi
  if [ "$COND" = H ]; then cat_heat_to "$HOLD" "$PREHEAT_MAX_LAUNCHES" "$OUT/preheat.jsonl" || true; fi
fi

# the sampler's own time limit is only a backstop (stop_sampler ends it); 5 min above the runner's bound
start_sampler "$OUT/telemetry.jsonl" $((MAXS + 300)) || { finish fail "sampler would not start"; exit 1; }
# --tel-live: the file lib's start_sampler has the sampler write (stop_sampler folds it into telemetry.jsonl)
rargs=("$OUT" --root "$V3_ROOT" --only "$ONLY" --passes 1 $TIMING --seed "$SEED" --host-bin "$HOST_BIN"
       --tel-live "$OUT/telemetry.jsonl.raw" --card "$CARD")
[ -n "$HOLD" ] && rargs+=(--hold-hot "$HOLD" --heater "$HEATER")
[ -n "$SMOKE" ] && rargs+=(--hold-max 1 --hold-limit 1)
if [ -n "${V3_DRY:-}" ]; then
  python3 "$RUNNER" "${rargs[@]}" --dry; rc=$?
else
  python3 "$RUNNER" "${rargs[@]}" > "$OUT/runner.out" 2>&1; rc=$?
fi
stop_sampler
[ "$rc" = 3 ] && yield_exit "another user or device process appeared during the pass (runner stopped)"

if [ -n "${V3_DRY:-}" ]; then
  st=ok; note="dry run (runner rc $rc)"
else
  res=$(python3 "$HERE/catlib.py" check "$OUT" --card "$CARD" --root "$V3_ROOT" 2>&1) || res="fail post-pass check crashed: ${res//\"/\'}"
  st=${res%% *}; note=${res#* }
  [ $rc -eq 4 ] && { st=fail; note="the sampler stopped writing: runner stopped the pass; $note"; }
  [ $rc -ne 0 ] && [ "$st" != fail ] && { st=fail; note="runner rc $rc; $note"; }
fi
gz_out
finish "$st" "${note//\"/\'}"
[ "$st" = ok ] && exit 0
[ -n "$SMOKE" ] && [ "$st" = offclock ] && exit 0    # smoke checks the pipeline, not the clock
exit 1
