#!/usr/bin/env bash
# V3-LAT (PLAN3.md §2 "V3-LAT", plan3.json experiments[V3-LAT]): one block of the latency, cycle-count and
# bandwidth sweeps on the local card (memhier chases, nocbench, sparsity cycle counts and extras, enercat lone-minion
# streams, sgemm, the hot-line sweep, the relay sweep; on aifoundry2 also V3-COOL's steady-600 warm controls).
# Runs on aifoundry2, aifoundry3 and aifoundry1's two cards (V3_DEVICE=0 or 1 on aifoundry1; lib.sh names the card).
#
#   bash tools/claims-v3/lat/block.sh <pass> [--smoke]
#
# <pass>  1 2 3        a whole pass K in one block (re-runs of a dropped pass: 6 7 8 9)
#         K1 K2        the first / second half of pass K (11 12 21 22 31 32; 61 62 ... 92): the same unit order,
#                      cut in two by estimated card time, so each block stays well under 35 min on aifoundry2
#         4 5          a divergence-only short block (E4 (f): passes 1-3 + these two = the 5 registered blocks;
#                      re-runs: 41-49)
# --smoke              the smallest real check of every component (under a minute of card time); data go to
#                      $DATA_ROOT/lat-smoke/p<pass>
# V3_DRY=1 prints every device call instead of running it (lib.sh). LAT_SCPSELF=1 adds the optional scpself
# bus-error probe (and the health launch after it) at the end of the hot-line unit; it is off by default.
# README.md in this directory says what a pass does, what is dropped, and every deviation from the plan.
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"      # cd's to the tree root, sets CARD, binaries, DATA_ROOT
others_present && exit 3
# a device process of ours still on this card (with V3_DEVICE set, lib.sh counts only this card's): not starting
ours_running && { log "a device process of ours on this card is still running: not starting"; exit 3; }
# On a host with several cards (V3_DEVICE set) lib.sh's drain_mgmt must not run: /opt/et/bin/dev_mngt_service is not
# ET_DEVICES-filtered and opens every card, so it would reach the other card while that card's queue holds its
# management node (the two-openers case). heat_to, start_sampler and stop_sampler call it by name, so this also
# covers them; a management node that stays stuck then fails the unit (samp) instead of being drained.
if [ -n "${V3_DEVICE:-}" ]; then
  drain_mgmt() { log "drain_mgmt skipped (V3_DEVICE=$V3_DEVICE: dev_mngt_service opens every card)"; }
fi

ARG=${1:?usage: block.sh <pass> [--smoke]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
LATDIR=tools/claims-v3/lat
if [[ ! "$ARG" =~ ^[0-9]+$ ]]; then echo "bad pass '$ARG'" >&2; exit 2; fi
if [ -n "$SMOKE" ]; then KIND=smoke; K=$ARG; HALF=0
elif [[ "$ARG" =~ ^[1236789]$ ]]; then KIND=full; K=$ARG; HALF=0
elif [[ "$ARG" =~ ^[1236789][12]$ ]]; then KIND=half; K=${ARG:0:1}; HALF=${ARG:1:1}
elif [[ "$ARG" =~ ^(4|5|4[1-9])$ ]]; then KIND=div; K=$ARG; HALF=0
else echo "bad pass '$ARG' (1-3, 6-9, K1/K2, 4, 5, 41-49)" >&2; exit 2; fi

# Per-card parameters (README "Four cards"). lib.sh sets GOV_FREE on every card but aifoundry3, whose clock a boot
# service pins at 600 MHz. A governor-free card is heated to HEAT_C before every unit, nocbench invocation and
# sparsity group, and its launches off 600 MHz are dropped by the reducer; aifoundry1's two cards take aifoundry2's
# target. V3-COOL's warm controls (unit c6) run where V3-COOL is registered, aifoundry2 only.
# IDLE_MHZ: the idle point known before any run (reduce.py REGISTERED_IDLE), the low-power operating point of
# aifoundry1's cards (300 MHz / 398 mV, queried on c0, firmware 1.4.1, 25 Sep); the idle probes add what they read
# below 600 MHz. WITNESS: the card idles below 600 MHz between kernels, so its divergence blocks carry clock witnesses.
case "$CARD" in
  aifoundry3)    HEAT_C=;   IDLE_MHZ=;    WITNESS=;  COOL_CONTROLS= ;;    # pinned at 600 MHz: never heated
  aifoundry2)    HEAT_C=76; IDLE_MHZ=;    WITNESS=;  COOL_CONTROLS=1 ;;   # governor free, TDP 65 W, 65 C; idles at 600
  aifoundry1-c0) HEAT_C=76; IDLE_MHZ=300; WITNESS=1; COOL_CONTROLS= ;;    # as aifoundry2; idles at 300 ("low_power")
  aifoundry1-c1) HEAT_C=76; IDLE_MHZ=300; WITNESS=;  COOL_CONTROLS= ;;    # as aifoundry2; seen idling at 600 MHz
  *)             HEAT_C=76; IDLE_MHZ=;    WITNESS=;  COOL_CONTROLS= ;;
esac

pause() { [ -n "${V3_DRY:-}" ] || sleep "$1"; }
mark() {  # mark <event> <unit> [note]
  printf '{"t_ms":%s,"ev":"%s","unit":"%s","note":"%s","pass":%s}\n' "$(now_ms)" "$1" "$2" "${3:-}" "$ARG" >> "$OUT/marks.jsonl"
}
NOTES=()
note() { NOTES+=("$*"); log "note: $*"; }

# Stop at once if another user logs in or another user's device process appears: the block ends as failed and
# exits 3, so queue.sh moves the partial pass aside and retries it later.
guard() {
  if others_present; then
    stop_sampler; mark others_arrived "${U:-}" "$1"
    block_end fail "others arrived before $1"; exit 3
  fi
}

# One device process as run_lab.sh's run(): stdout -> <name>.jsonl, stderr -> <name>.err, exit code and host-side
# start/end times -> launches.jsonl (the reducer's clock window for lines that carry no timestamps).
run1() {  # run1 <name> <cmd> [args...]
  local name=$1 t0 rc; shift
  guard "$name"; t0=$(now_ms)
  if [ -n "${V3_DRY:-}" ]; then hold10 "$@" > "$UD/$name.jsonl"; rc=$?
  else hold10 "$@" > "$UD/$name.jsonl" 2> "$UD/$name.err"; rc=$?; fi
  printf '{"name":"%s","rc":%s,"t0_ms":%s,"t1_ms":%s}\n' "$name" "$rc" "$t0" "$(now_ms)" >> "$UD/launches.jsonl"
  [ "$rc" = 124 ] && note "$U/$name timed out (timeout 10)"
  [ -n "${V3_DRY:-}" ] || log "  $U/$name rc=$rc ok=$(grep -c '"ok":true' "$UD/$name.jsonl") bad=$(grep -c '"ok":false' "$UD/$name.jsonl")"
  return 0
}
# One labelled launch appended to a sweep file, as E-HL1's nb() / E-RL1's on(): the host's "PREFIX {" becomes
# {"group":G,"cfg":ID,"host":CARD,"pass":K, ...
run_lab1() {  # run_lab1 <out.jsonl> <PREFIX> <group> <cfg-id> <cmd> [args...]
  local f=$1 pre=$2 g=$3 id=$4 t0 rc; shift 4
  guard "$g/$id"; t0=$(now_ms)
  if [ -n "${V3_DRY:-}" ]; then hold10 "$@" > /dev/null; rc=$?
  else
    hold10 "$@" 2>> "$UD/stderr.log" | grep "^$pre {" |
      sed "s/^$pre {/{\"group\":\"$g\",\"cfg\":$id,\"host\":\"$CARD\",\"pass\":$K,/" >> "$f"
    rc=${PIPESTATUS[0]}
  fi
  printf '{"name":"%s","cfg":%s,"rc":%s,"t0_ms":%s,"t1_ms":%s}\n' "$g" "$id" "$rc" "$t0" "$(now_ms)" >> "$UD/launches.jsonl"
  [ "$rc" = 124 ] && note "$U/$g cfg $id timed out (timeout 10)"
  return 0
}

# Units. unit_begin heats a governor-free card to >= HEAT_C (heat_to reads the die through the management node, so
# the sampler is stopped first), records the idle clock, and starts the unit's 10 Hz sampler; rewarm does the same
# between groups of a unit.
U=; UD=
warm() {  # governor-free card: heat_to HEAT_C, unless the die cannot be read (heat_to would then loop 150 launches)
  [ -n "$GOV_FREE" ] || return 0
  if [ -z "$(die_c)" ]; then drain_mgmt; [ -n "$(die_c)" ] || { note "$1: die unreadable, not heated"; return 0; }; fi
  heat_to "$HEAT_C" "$OUT/heat.jsonl" || note "$1: heat_to $HEAT_C gave up"
}
# The card's clock at rest, read once before each sampler start (every card): aifoundry1-c0's firmware idles the
# minions at 300 MHz between kernels, and the reducer sets samples at a card's idle point aside (README "Four cards").
idle_probe() {  # idle_probe <label>  -> $OUT/idle.jsonl {"t_ms","unit","mhz"} (mhz null if the node did not answer)
  local m; m=$(clock_mhz)
  printf '{"t_ms":%s,"unit":"%s","mhz":%s,"pass":%s}\n' "$(now_ms)" "$1" "${m:-null}" "$ARG" >> "$OUT/idle.jsonl"
}
samp() {  # samp <label>: start the unit's sampler. On a governor-free card a unit without one is useless (every
  # launch would be dropped for want of a clock reading) and the management node is probably stuck: the block stops.
  start_sampler "$UD/telemetry.jsonl" 900 && return 0
  note "$1: sampler failed to start"
  if [ -n "$GOV_FREE" ]; then mark sampler_failed "$U" "$1"; block_end fail "sampler failed at $1"; exit 1; fi
}
unit_begin() {  # unit_begin <unit> [nosampler]
  U=$1; UD=$OUT/$U; rm -rf "${UD:?}"; mkdir -p "$UD"; guard "$U"   # one attempt per pass dir (V3_FORCE re-runs)
  mark begin "$U"
  warm "$U"
  idle_probe "$U"
  [ "${2:-}" = nosampler ] && return 0
  samp "$U"
}
rewarm() {  # rewarm <label>: governor-free cards only; aifoundry3's sampler keeps running
  [ -n "$GOV_FREE" ] || return 0
  stop_sampler; mark rewarm "$U" "$1"
  warm "$U/$1"
  idle_probe "$U/$1"
  samp "$U/$1"
}
# The drop rule, made visible at the block (governor-free cards): a unit whose samples (unit sampler or sgemm
# brackets) read mhz.minion != 600 gets an "off600" mark with the clocks seen; if any of them is not the card's idle
# point (a reading below 600 MHz of this block's idle probes), a note goes into block.json, so the operator knows a
# pass may need a re-run (6-9 / K1-K2 halves) without running reduce.py first. The reducer decides launch by launch.
off600() { sed -n 's/.*"mhz":{"minion":\([0-9]*\).*/\1/p' "$1" 2>/dev/null | grep -cvx 600; }
offhist() { sed -n 's/.*"mhz":{"minion":\([0-9]*\).*/\1/p' "$1" 2>/dev/null | grep -vx 600 | sort -n | uniq -c |
            awk '{printf "%s%sx%s", (NR > 1 ? " " : ""), $2, $1}'; }
idle_points() { { sed -n 's/.*"mhz":\([0-9]*\).*/\1/p' "$OUT/idle.jsonl" 2>/dev/null; echo "${IDLE_MHZ:-}"; } |
                awk '$1 != "" && $1 < 600' | sort -un | tr '\n' ' '; }
unit_end() {
  stop_sampler
  if [ -n "$GOV_FREE" ] && [ -z "${V3_DRY:-}" ]; then
    local f n h ip nl
    ip=$(idle_points)
    for f in "$UD/telemetry.jsonl" "$UD/brackets.jsonl"; do
      [ -s "$f" ] || continue
      n=$(off600 "$f")
      if [ "${n:-0}" -gt 0 ]; then
        h=$(offhist "$f")
        mark off600 "$U" "$n of $(grep -c '^{' "$f") samples in $(basename "$f"): $h (idle point: ${ip:-none})"
        nl=$(sed -n 's/.*"mhz":{"minion":\([0-9]*\).*/\1/p' "$f" | awk -v ip=" $ip" '$1 != 600 && index(ip, " " $1 " ") == 0' | wc -l)
        [ "$nl" -gt 0 ] && note "$U: $nl samples off 600 MHz and off the idle point ($h): launches near them are dropped"
      fi
    done
  fi
  mark end "$U"; log "unit $U done"; U=; UD=
}

# ---------------------------------------------------------------- memhier (workloads/memhier/run_lab.sh groups)
mh() { local n=$1; shift; run1 "$n" "$MEMHIER" --budget 8 --test chase "$@"; pause 3; }
u_mc() {  # group chase: 9 processes
  unit_begin mc
  mh chase-dram                                     # 256 B to 256 MB from shire 0
  mh chase-dram-sweep-from24 --chaser-shire 24
  mh chase-dram-thread1 --thread 1 --sizes 256,512,768,1K,4K
  for s in 7 24 31; do mh "chase-dram-from$s" --chaser-shire $s --sizes 4M,256M; done
  mh chase-dram-from0-repeat --sizes 4M,256M
  mh chase-dram-placement --steps 20000 --sizes 4M,4M,4M,4M,4M,4M,4M,4M,256M,4M,4M,4M,4M,256M
  mh chase-dram-offsets --steps 20000 --sizes 128M,128M,128M,128M,128M,128M,128M,128M
  unit_end
}
u_ms() {  # group scp: 5 processes
  unit_begin ms
  mh chase-scp-local --where scp --scp-shire local --sizes 256,512,768,1K,2K,4K,8K,16K,64K,256K,1M,2M
  mh chase-scp-map --where scp --scp-shire all --sizes 64K
  for s in 7 24 31; do mh "chase-scp-map-from$s" --where scp --scp-shire all --sizes 64K --chaser-shire $s; done
  unit_end
}

# ---------------------------------------------------------------- nocbench (workloads/nocbench/run_lab.sh groups)
CLASSES=0.0-0.1,0.0-0.2,0.0-0.4,0.0-0.3,0.0-0.5,0.0-0.6,0.0-0.7,0.1-0.2,0.0-0.8,0.0-0.16,0.0-0.24,0.0-0.31,0.0-8.0,0.0-24.0,0.0-1.0,0.0-5.0,0.0-31.0
SHORT=0.0-0.1,0.0-0.7,0.0-8.0,0.0-31.0
LOADED=$(for s in $(seq 0 15); do printf '%s.0-%s.0,' $s $((s + 16)); done); LOADED=${LOADED%,}
nr() { local n=$1; shift; run1 "$n" "$NOCBENCH" --budget 8 "$@"; pause 3; }
noc_group() {
  case $1 in
  classes)
    nr classes-pingpong --test pairs --pairs $CLASSES --counts 1 --iters 4000 --warmup 100
    nr classes-fcc --test pairs --mode fcc --pairs $CLASSES --iters 4000 --warmup 100
    nr classes-flag --test pairs --mode flag --pairs $CLASSES --iters 2000 --warmup 50 ;;
  counts)
    nr counts-pingpong --test pairs --pairs $SHORT --counts 1,2,4,8,16,24,32,48,64,96,127 --iters 2000 --warmup 50 ;;
  stream)
    nr counts-stream --test pairs --mode stream --pairs $SHORT --counts 1,2,4,8,16,24,32,48,64,96,127 --iters 4000 --warmup 50 ;;
  functs)
    for f in iadd imax fadd fmax; do
      nr "functs-$f" --test pairs --pairs 0.0-0.1,0.0-8.0 --counts 1,32 --funct $f --iters 2000 --warmup 50
    done ;;
  matrix)
    nr matrix-pingpong --test matrix --iters 300 --warmup 20
    nr matrix-pingpong-m31 --test matrix --minion 31 --iters 300 --warmup 20
    nr matrix-pingpong-c32 --test matrix --count 32 --iters 300 --warmup 20
    nr intra-pingpong --test intra --shire 0 --iters 300 --warmup 20
    nr intra-pingpong-s24 --test intra --shire 24 --iters 300 --warmup 20 ;;
  sync)
    nr fcc-inshire-block --test pairs --mode fcc --pairs 0.0-0.1,0.0-0.7,0.0-0.8,0.0-0.31 --iters 4000 --warmup 100
    nr fcc-inshire-poll --test pairs --mode fcc --pairs 0.0-0.1,0.0-0.7,0.0-0.8,0.0-0.31 --iters 4000 --warmup 100 --poll 1
    nr matrix-fcc --test matrix --mode fcc --iters 300 --warmup 20
    nr matrix-flag --test matrix --mode flag --iters 200 --warmup 10 ;;
  allreduce)
    for c in 1 8 32; do
      nr "allreduce-c$c" --test allreduce --count $c --iters 1000 --shires 0x1
      nr "allreduce-all-c$c" --test allreduce --count $c --iters 1000
    done ;;
  xallreduce)
    for c in 1 32; do nr "xallreduce-c$c" --test allreduce --levels 6,7,8,9,10 --count $c --iters 500; done ;;
  barrier)
    nr barrier-shire1 --test barrier --scope shire --shires 0x1 --iters 4000 --warmup 100
    nr barrier-shire32 --test barrier --scope shire --iters 4000 --warmup 100
    nr barrier-chip1 --test barrier --scope chip --per-shire 1 --iters 2000 --warmup 50
    nr barrier-chip32 --test barrier --scope chip --iters 2000 --warmup 50 ;;
  loaded)
    nr isolated-pairs --test pairs --pairs $LOADED --counts 1,32 --iters 2000 --warmup 50
    nr loaded-pairs --test pairs --concurrent --pairs $LOADED --counts 1,32 --iters 2000 --warmup 50 ;;
  esac
}
u_noc() {  # all 10 groups in the three invocations of the a2 plan (heat before each); even passes reverse them
  local G=(classes counts stream functs matrix sync allreduce barrier xallreduce loaded) g i
  if [ $((K % 2)) = 0 ]; then G=(loaded xallreduce barrier allreduce sync matrix functs stream counts classes); fi
  unit_begin noc
  for i in 0 1 2 3 4 5 6 7 8 9; do
    { [ $i = 4 ] || [ $i = 6 ]; } && rewarm "invocation-$((i < 6 ? 2 : 3))"
    mark group "$U" "${G[$i]}"; noc_group "${G[$i]}"
  done
  unit_end
}

# ---------------------------------------------------------------- sparsity (workloads/sparsity/run_lab.sh groups)
SWEEP=0,0.125,0.25,0.375,0.5,0.625,0.75,0.875,0.9375,1
ONE="--shires 0x1 --per-shire 1"
ALL="--shires 0xFFFFFFFF --per-shire 32"
sr() { local n=$1; shift; run1 "$n" "$SPARSITY" --budget 8 "$@"; pause 2; }
sp_group() {
  case $1 in
  fma)
    for p in elem col row; do sr "fma-fp32-$p" --test fma --type fp32 --pattern $p --sweep $SWEEP $ONE; done
    sr fma-fp32-elem-tenb --test fma --type fp32 --pattern elem --sweep $SWEEP --b-stream $ONE
    sr fma-fp32-bsparse --test fma --type fp32 --pattern none --sweep 0 --b-sparsity 0.5 $ONE
    sr fma-fp32-bsparse90 --test fma --type fp32 --pattern none --sweep 0 --b-sparsity 0.9 $ONE
    for m in 0xFFFF 0x00FF 0x000F 0x0001 0x0000; do
      sr "fma-fp32-rowmask-$m" --test fma --type fp32 --pattern none --sweep 0 --row-mask $m $ONE
    done
    sr fma-fp16-elem --test fma --type fp16 --pattern elem --sweep $SWEEP $ONE
    sr fma-fp16-pair --test fma --type fp16 --pattern pair --sweep 0,0.5,1 $ONE
    sr fma-int8-elem --test fma --type int8 --pattern elem --sweep $SWEEP $ONE
    sr fma-fp32-elem-all --test fma --type fp32 --pattern elem --sweep 0,0.5,0.875,1 $ALL --iters 4000 ;;
  tload)
    for w in dram l2 scp; do
      sr "tload-$w-one" --test tload --where $w --masks 0xFFFF,0x7FFF,0xFF,0xF,0x3,0x1,0x0 $ONE --iters 20000
      sr "tload-$w-all" --test tload --where $w --masks 0xFFFF,0xFF,0xF,0x1,0x0 $ALL --iters 2000
    done ;;
  gemv)
    sr gemv-dense --test gemv --gemv dense --sweep 0,0.5,0.75,0.9,0.95,0.99,1 $ALL --iters 2000
    sr gemv-masked --test gemv --gemv masked --sweep 0,0.5,0.75,0.9,0.95,0.99,1 $ALL --iters 2000
    sr gemv-skip --test gemv --gemv skip --sweep 0,0.5,0.75,0.9,0.95,0.99,1 $ALL --iters 2000
    sr gemv-skip-oneshire --test gemv --gemv skip --sweep 0,0.9,0.99 --shires 0x1 --per-shire 32 --iters 2000
    for g in dense masked skip; do
      sr "gemv-tree-$g" --test gemv --gemv $g --gemv-tree --sweep 0,0.5,0.75,0.9,0.95,0.99,1 $ALL --iters 2000
    done
    sr gemv-tree-oneshire --test gemv --gemv skip --gemv-tree --sweep 0,0.9,0.99 --shires 0x1 --per-shire 32 --iters 2000 ;;
  diverge)
    for a in 0 3 2 1.5 1.2; do
      for v in static refill scalar; do
        sr "diverge-$v-a$a" --test diverge --variant $v --alpha $a --mean-k 64 --kmax 16384 --items 256 --harts 2 $ALL
      done
    done ;;
  esac
}
u_sp() {
  local g first=1
  unit_begin sp
  for g in fma tload gemv diverge; do
    [ -n "$first" ] || rewarm "$g"; first=
    mark group "$U" "$g"; sp_group "$g"
  done
  unit_end
}
div_subset() {  # E4 (f): the page's draw (seed 1), refill and static at alpha 3 and 2
  local a v
  for a in 3 2; do
    for v in static refill; do
      sr "div-$v-a$a" --test diverge --variant $v --alpha $a --mean-k 64 --kmax 16384 --items 256 --harts 2 $ALL --seed 1
    done
  done
}
u_e4x() {  # E4 extras (i) probe lengths, (ii) layer draws 2 and 3, (iii) the divergence subset
  local n
  unit_begin e4x
  for n in 2000 20000 200000; do sr "tload-l2-all-n$n" --test tload --where l2 --masks 0xFFFF $ALL --iters $n; done
  for n in 2000 20000; do sr "tload-dram-all-n$n" --test tload --where dram --masks 0xFFFF $ALL --iters $n; done
  for n in 2 3; do sr "gemv-tree-skip-seed$n" --test gemv --gemv skip --gemv-tree --sweep 0.9,0.95,0.99 $ALL --iters 2000 --seed $n; done
  div_subset
  unit_end
}
# Clock witnesses (README "Four cards"): a divergence-only short block has four 2 ms kernels and nothing else, so on a
# card that idles below 600 MHz between kernels (aifoundry1-c0: 300 MHz) its samples are all idle and the reducer has
# no reading of the burst clock. There the block adds one 85 ms all-minion TensorLoad (E4 extra (i)'s 200,000-load
# probe) before and after the subset: samples inside it and its cycles / wall time give the unit's busy clock.
witness_needed() {
  [ -n "$WITNESS" ] && return 0
  [ -n "$GOV_FREE" ] && [ -n "$(sed -n 's/.*"mhz":\([0-9]*\).*/\1/p' "$OUT/idle.jsonl" 2>/dev/null | tail -1 | awk '$1 < 600')" ]
}
witness() { sr "witness-$1" --test tload --where l2 --masks 0xFFFF $ALL --iters 200000; }
u_div() {
  local w=
  unit_begin div
  witness_needed && w=1
  [ -n "$w" ] && witness 1
  div_subset
  [ -n "$w" ] && witness 2
  unit_end
}

# ---------------------------------------------------------------- ridge-X3: enercat lone-minion DRAM streams
u_x3() {
  local m sm
  unit_begin x3
  for m in $(printf '32\n1\n' | shuf --random-source=<(yes "$K")); do
    if [ "$m" = 32 ]; then sm=0xffffffff; else sm=0x1; fi
    run1 "x3-m$m" "$ENERCAT" --budget 8 --pattern tload_pat --operands random --shires $sm --minions 0x1 \
      --slice-bytes 64M --region 64M --stride 1K --access-bytes 1K --seconds 3 --window 240000000
    pause 3
  done
  unit_end
}

# ---------------------------------------------------------------- E5: sgemm (opens /dev/et0_mgmt itself)
# sgemm_host creates its device layer with the management node (workloads/sgemm/host/main.cpp:49), so no sampler
# may run during it: the clock is read by a short sampler burst right before and right after each process (one
# burst between two processes serves as the first's "after" and the second's "before": 5 sampler starts per unit,
# not 8, since a start right after a previous instance often fails and costs a retry).
bracket() { start_sampler "$UD/brackets.jsonl" 5 || note "$U: bracket sampler failed"; pause 1; stop_sampler; }
u_sg() {
  local i=0 a t0 rc
  local TIMEV=(); [ -x /usr/bin/time ] && TIMEV=(/usr/bin/time -v)
  [ ${#TIMEV[@]} = 0 ] && note "sg: no /usr/bin/time, no peak RSS"
  unit_begin sg nosampler
  bracket                        # the first process's "before" burst
  for a in "-n 64 --shires 0x1" "-n 512 --shires 0x1" "-n 512" "-n 1024"; do
    i=$((i + 1)); guard "sgemm-$i"
    mark sgemm "$U" "$i: $a"; t0=$(now_ms)
    # shellcheck disable=SC2086
    if [ -n "${V3_DRY:-}" ]; then hold10 "${TIMEV[@]}" "$SGEMM" $a --reps 3; rc=$?
    else hold10 "${TIMEV[@]}" "$SGEMM" $a --reps 3 > "$UD/sgemm-$i.log" 2>&1; rc=$?; fi
    printf '{"name":"sgemm-%s","args":"%s","rc":%s,"t0_ms":%s,"t1_ms":%s}\n' "$i" "$a" "$rc" "$t0" "$(now_ms)" >> "$UD/launches.jsonl"
    [ "$rc" = 124 ] && note "sg/sgemm-$i timed out"
    bracket; pause 2              # this process's "after" burst, and the next one's "before" (reduce.py: within 10 s)
  done
  unit_end
}

# ---------------------------------------------------------------- E-HL1: the hot-line sweep
hl_configs() {  # "group|args" lines: run_hotline.sh's 42, then the plan's extras
  local h n m p w W
  for h in 0 7 15 31; do echo "fairness|--home $h --shires 0xffffffff --per-shire 32"; done
  echo "fairness|--home 0 --shires 0xffffffff --per-shire 1"
  for h in 0 scp:0 own scp:own; do echo "placement|--home $h --shires 0xffffffff --per-shire 32"; done
  for h in scplocal:0 dramlocal:0 scpstream:0 dramstream:0; do
    echo "local|--home $h --shires 0x1 --per-shire 32"; echo "local|--home $h --shires 0xffffffff --per-shire 32"
  done
  for n in 1 2 4 8 12 16 20 24 32; do echo "requesters|--home scplocal:0 --shires 0x3 --per-shire $n"; done
  for m in 0x3 0x7 0x1f 0x1ff 0x1ffff 0xffffffff; do echo "shires|--home scplocal:0 --shires $m --per-shire 32"; done
  for p in 0 1000 4000 8000 10000 12000 16000 20000 40000 100000; do
    echo "pace|--home scplocal:0 --shires 0xffffffff --per-shire 32 --pace $p"
  done
  for n in 19 21 22 23; do echo "req|--home scplocal:0 --shires 0x3 --per-shire $n"; done
  for n in 1 2 4 8 12 16 19 20 21 22 23 24; do echo "alone|--home scplocal:0 --shires 0x1 --per-shire $n"; done
  for p in 9000 9500 9800 10500; do echo "pace|--home scplocal:0 --shires 0xffffffff --per-shire 32 --pace $p"; done
  for h in scplocal:0 dramlocal:0 scpstream:0 dramstream:0; do
    for W in 3000000 24000000 60000000; do echo "win|--home $h --shires 0xffffffff --per-shire 32 --window $W"; done
  done
  echo "poll|--home scplocal:0 --shires 0xffffffff --per-shire 1"
  for w in 0 10; do echo "warm|--home scplocal:0 --shires 0xffffffff --per-shire 32 --warmup $w"; done
}
u_hl() {
  local line id g args
  unit_begin hl
  hl_configs | awk '{print NR "|" $0}' > "$UD/configs.txt"
  shuf --random-source=<(yes "$K") "$UD/configs.txt" > "$UD/order.txt"
  while IFS='|' read -r id g args; do
    # shellcheck disable=SC2086
    run_lab1 "$UD/sweep.jsonl" NOCBENCH "$g" "$id" "$NOCBENCH" --test hotline --warmup 5 --window 6000000 --pace 0 $args
  done < "$UD/order.txt"
  if [ -n "${LAT_SCPSELF:-}" ]; then   # optional, last: expect a kernel bus error, then one plain launch must work
    run_lab1 "$UD/sweep.jsonl" NOCBENCH self 901 "$NOCBENCH" --test hotline --warmup 5 --window 6000000 --pace 0 \
      --home scpself:0 --shires 0xffffffff --per-shire 32
    run_lab1 "$UD/sweep.jsonl" NOCBENCH health 902 "$NOCBENCH" --test hotline --warmup 5 --window 6000000 --pace 0 \
      --home 0 --shires 0xffffffff --per-shire 32
    if [ -z "${V3_DRY:-}" ] && ! grep -q '"group":"health".*"ok":true' "$UD/sweep.jsonl"; then
      note "hl: the health launch after the scpself probe failed: stop and report"
      unit_end; block_end fail "health launch after scpself failed"; exit 1
    fi
  fi
  unit_end
}

# ---------------------------------------------------------------- E-RL1: the relay sweep
rl_configs() {  # "group|args": 2 probes, run_onchip.sh's 86 relay rows, 31 offsets
  local m med w b k d
  for m in 0 1; do echo "probe|--test probe --method $m --shift 1"; done
  r() { echo "$1|--test relay --medium $2 --stage-bytes $3 --stages $4 --work $5 --shires $6 --hop-distance ${7:-1}"; }
  for med in dram scp hop; do r headline $med 1M 8 1 0xffffffff; done
  for w in 1 2 4 8 16 32 64 128 256; do for med in dram scp hop; do r intensity $med 1M 8 "$w" 0xffffffff; done; done
  for b in 64K 128K 256K 512K 1M; do for med in dram scp hop; do r size $med "$b" 8 1 0xffffffff; done; done
  for k in 1 2 4 8 16 32; do for med in dram scp hop; do r stages $med 1M "$k" 1 0xffffffff; done; done
  for m in 0x3 0xf 0xff 0xffff 0xffffffff; do for med in dram scp hop; do r shires $med 1M 8 1 "$m"; done; done
  for d in 1 2 4 8 16; do r distance hop 1M 8 1 0xffffffff "$d"; done
  for b in 2M 4M 8M; do r bigsize dram "$b" 8 1 0xffffffff; done
  for d in $(seq 1 31); do r offsets hop 1M 8 1 0xffffffff "$d"; done
}
u_rl() {
  local id g args
  unit_begin rl
  rl_configs | awk '{print NR "|" $0}' > "$UD/configs.txt"
  shuf --random-source=<(yes "$K") "$UD/configs.txt" > "$UD/order.txt"
  while IFS='|' read -r id g args; do
    # shellcheck disable=SC2086
    run_lab1 "$UD/sweep.jsonl" ONCHIP "$g" "$id" "$ONCHIP" $args
  done < "$UD/order.txt"
  unit_end
}

# ---------------------------------------------------------------- aifoundry2: V3-COOL's steady-600 warm controls
# The warm block of E-HL2 (tools/ettelem/run_hotline_power.sh with timeout 10, its own sampler) and E-RL2 (20 DRAM
# --stages 640 + 10 hop --stages 7800 relay launches), for V3-COOL's reducer; LAT's reducer does not use them.
u_c6() {
  local lab home sh ps rep i
  unit_begin c6
  pause 8                                                    # the runner's idle stretch before anything runs
  for spec in "contended 0 0xffffffff 32" "spread own 0xffffffff 32" "contended_scp scp:0 0xffffffff 32" \
              "starved scplocal:0 0xffffffff 32" "local_only scplocal:0 0x1 32"; do
    read -r lab home sh ps <<< "$spec"
    printf '{"label":"%s","t_ms":%s}\n' "$lab" "$(now_ms)" >> "$UD/marks.jsonl"
    for rep in 1 2 3; do
      guard "c6/$lab"
      if [ -n "${V3_DRY:-}" ]; then
        hold10 "$NOCBENCH" --test hotline --home "$home" --shires "$sh" --per-shire "$ps" --window 1200000000 --warmup 5
      else
        hold10 "$NOCBENCH" --test hotline --home "$home" --shires "$sh" --per-shire "$ps" --window 1200000000 --warmup 5 \
          2>> "$UD/stderr.log" | grep '^NOCBENCH {' | sed "s/^NOCBENCH {/{\"label\":\"$lab\",\"rep\":$rep,/" >> "$UD/runs.jsonl"
      fi
    done
    pause 10
  done
  pause 6
  for i in $(seq 1 20); do
    run_lab1 "$UD/relay.jsonl" ONCHIP rl2-dram "$i" "$ONCHIP" --test relay --medium dram --stage-bytes 1M --stages 640 --work 1
  done
  for i in $(seq 1 10); do
    run_lab1 "$UD/relay.jsonl" ONCHIP rl2-hop "$i" "$ONCHIP" --test relay --medium hop --stage-bytes 1M --stages 7800 --work 1
  done
  unit_end
}

# ---------------------------------------------------------------- the pass's units and their order
# Estimated aifoundry2 minutes per unit (heating included), used only to cut a pass into two halves.
declare -A EST=([mc]=4 [ms]=2.5 [noc]=6 [sp]=7 [e4x]=2 [x3]=1.5 [sg]=1.5 [hl]=2.5 [rl]=2.5 [c6]=3.5)
unit_order() {  # prints this block's units, one per line
  local order cut
  order=$(printf '%s\n' mc ms noc sp e4x x3 sg hl rl | shuf --random-source=<(yes "$K"))
  # the cut that best balances the two halves' estimated minutes (common units only, so both cards cut alike)
  cut=$(echo "$order" | awk -v est="$(for u in "${!EST[@]}"; do printf '%s=%s ' "$u" "${EST[$u]}"; done)" '
    BEGIN { n = split(est, kv, " "); for (i = 1; i <= n; i++) { split(kv[i], p, "="); w[p[1]] = p[2] } }
    { u[NR] = $1; tot += w[$1] }
    END { best = 1e9; s = 0; for (i = 1; i < NR; i++) { s += w[u[i]]; d = (2 * s - tot); if (d < 0) d = -d;
          if (d < best) { best = d; c = i } } ; print c }')
  local h1 h2
  h1=$(echo "$order" | head -n "$cut"); h2=$(echo "$order" | tail -n +"$((cut + 1))")
  if [ -n "$COOL_CONTROLS" ]; then   # c6 (aifoundry2) joins the lighter half (ties: the second)
    local s1 s2
    s1=$(for u in $h1; do echo "${EST[$u]}"; done | awk '{s += $1} END {print s + 0}')
    s2=$(for u in $h2; do echo "${EST[$u]}"; done | awk '{s += $1} END {print s + 0}')
    if awk -v a="$s1" -v b="$s2" 'BEGIN { exit !(a < b) }'; then h1=$(printf '%s\nc6' "$h1"); else h2=$(printf '%s\nc6' "$h2"); fi
  fi
  case $KIND in
  full) printf '%s\n%s\n' "$h1" "$h2" ;;
  half) if [ "$HALF" = 1 ]; then echo "$h1"; else echo "$h2"; fi ;;
  div) echo div ;;
  esac
}

# ---------------------------------------------------------------- smoke: every component once, < 60 s of card time
# (plus heating to HEAT_C on a governor-free card whose die is cooler, so the smoke sees the passes' conditions)
# The smoke's clock readout: the sampler's readings inside the launches' kernel windows (bursts) and outside them
# (idle). A card whose bursts do not read 600 MHz on a heated die would have every pass launch dropped (README "Four
# cards": aifoundry1-c0 idles at 300 MHz, and its bursts on a die above 65 C may stay there).
smoke_clock() {
  python3 - "$UD" <<'PYEOF'
import collections, glob, json, os, sys
d = sys.argv[1]
win = []
for p in glob.glob(os.path.join(d, "*.jsonl")):
    if os.path.basename(p) in ("telemetry.jsonl", "brackets.jsonl", "launches.jsonl"):
        continue
    for line in open(p):
        i = line.find("{")
        try:
            r = json.loads(line[i:]) if i >= 0 else {}
        except ValueError:
            continue
        if isinstance(r.get("t_start_ms"), (int, float)):
            win.append((r["t_start_ms"], r.get("t_end_ms") or r["t_start_ms"]))
busy, idle = collections.Counter(), collections.Counter()
for line in open(os.path.join(d, "telemetry.jsonl")):
    try:
        r = json.loads(line)
        t, m = r["t_ms"], r["mhz"]["minion"]
    except (ValueError, KeyError, TypeError):
        continue
    (busy if any(a <= t <= b for a, b in win) else idle)[m] += 1
print("minion MHz: inside kernel windows %s; outside %s" % (dict(sorted(busy.items())) or "no sample",
                                                            dict(sorted(idle.items())) or "no sample"))
PYEOF
}
smoke() {
  local S1 rc f
  U=smoke; UD=$OUT/smoke; rm -rf "${UD:?}"; rm -f "$OUT/marks.jsonl" "$OUT/idle.jsonl"; mkdir -p "$UD"; mark begin smoke
  log "smoke: die $(die_c) C, clock $(clock_mhz) MHz"
  if [ -n "$GOV_FREE" ]; then                                # heat_to's two parts: a die read (above), one heater launch
    run1 heater "$HEATER" --test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 1 --seed 1
    warm smoke                                               # then to HEAT_C, as before every pass unit
  fi
  idle_probe smoke
  start_sampler "$UD/telemetry.jsonl" 120 || note "smoke: sampler failed to start"
  run1 mh-chase "$MEMHIER" --budget 8 --test chase --sizes 4K,4M
  run1 mh-scp "$MEMHIER" --budget 8 --test chase --where scp --scp-shire local --sizes 64K
  run1 noc-pairs "$NOCBENCH" --budget 8 --test pairs --pairs 0.0-0.1,0.0-8.0 --counts 1 --iters 500 --warmup 10
  run_lab1 "$UD/hl.jsonl" NOCBENCH smoke 1 "$NOCBENCH" --test hotline --warmup 5 --window 6000000 --pace 0 --home scplocal:0 --shires 0x3 --per-shire 32
  run1 sp-fma "$SPARSITY" --budget 8 --test fma --type fp32 --pattern elem --sweep 0 --shires 0x1 --per-shire 1
  run1 sp-tload "$SPARSITY" --budget 8 --test tload --where dram --masks 0xFFFF --shires 0x1 --per-shire 1 --iters 2000
  run1 sp-gemv "$SPARSITY" --budget 8 --test gemv --gemv skip --gemv-tree --sweep 0.99 --shires 0xFFFFFFFF --per-shire 32 --iters 200 --seed 2
  run1 sp-div "$SPARSITY" --budget 8 --test diverge --variant refill --alpha 2 --mean-k 64 --kmax 16384 --items 256 --harts 2 --shires 0xFFFFFFFF --per-shire 32 --seed 1
  run1 x3-m32 "$ENERCAT" --budget 8 --pattern tload_pat --operands random --shires 0xffffffff --minions 0x1 \
    --slice-bytes 64M --region 64M --stride 1K --access-bytes 1K --seconds 1 --window 240000000
  run_lab1 "$UD/rl.jsonl" ONCHIP smoke 1 "$ONCHIP" --test probe --method 0 --shift 1
  run_lab1 "$UD/rl.jsonl" ONCHIP smoke 2 "$ONCHIP" --test relay --medium hop --stage-bytes 1M --stages 8 --work 1 --shires 0xffffffff --hop-distance 3
  if [ -n "$COOL_CONTROLS" ]; then
    run_lab1 "$UD/c6.jsonl" NOCBENCH c6 1 "$NOCBENCH" --test hotline --home scplocal:0 --shires 0xffffffff --per-shire 32 --window 1200000000 --warmup 5
    run_lab1 "$UD/c6.jsonl" ONCHIP c6 2 "$ONCHIP" --test relay --medium dram --stage-bytes 1M --stages 640 --work 1
  fi
  stop_sampler
  bracket
  S1=(); [ -x /usr/bin/time ] && S1=(/usr/bin/time -v)
  if [ -n "${V3_DRY:-}" ]; then hold10 "${S1[@]}" "$SGEMM" -n 64 --shires 0x1 --reps 1; rc=$?
  else hold10 "${S1[@]}" "$SGEMM" -n 64 --shires 0x1 --reps 1 > "$UD/sgemm.log" 2>&1; rc=$?; fi
  printf '{"name":"sgemm","rc":%s}\n' "$rc" >> "$UD/launches.jsonl"
  bracket
  mark end smoke
  if [ -n "${V3_DRY:-}" ]; then SMOKE_BAD="(dry: not checked)"; return 0; fi
  SMOKE_BAD=
  for f in mh-chase mh-scp noc-pairs hl sp-fma sp-tload sp-gemv sp-div x3-m32 rl $([ -n "$COOL_CONTROLS" ] && echo c6); do
    grep -q '"ok":true' "$UD/$f.jsonl" 2>/dev/null || SMOKE_BAD="$SMOKE_BAD $f"
  done
  grep -q '^PASS' "$UD/sgemm.log" || SMOKE_BAD="$SMOKE_BAD sgemm"
  [ -s "$UD/telemetry.jsonl" ] || SMOKE_BAD="$SMOKE_BAD sampler"
  [ -s "$UD/brackets.jsonl" ] || SMOKE_BAD="$SMOKE_BAD bracket"
  if [ -n "$GOV_FREE" ]; then grep -q '"rc":0' <(grep '"heater"' "$UD/launches.jsonl") || SMOKE_BAD="$SMOKE_BAD heater"; fi
  log "smoke idle probe: $(tail -1 "$OUT/idle.jsonl" 2>/dev/null)"
  [ -s "$UD/telemetry.jsonl" ] && log "smoke clock: $(smoke_clock 2>&1)"
  log "smoke launches (name rc):"; sed 's/^/    /' "$UD/launches.jsonl"
  log "smoke x3-m32 process seconds: $(awk -F'[:,}]' '/"x3-m32"/ {print ($8 - $6) / 1000}' "$UD/launches.jsonl")"
}

# ---------------------------------------------------------------- main
EXPN=lat; [ -n "$SMOKE" ] && EXPN=lat-smoke
block_begin "$EXPN" "$ARG"
sha256sum tools/claims-v3/lib.sh "$LATDIR"/* > "$OUT/code.sha256" 2>/dev/null || true
if [ "$KIND" = smoke ]; then
  smoke
  gzip -f "$OUT"/smoke/*.err "$OUT"/smoke/stderr.log 2>/dev/null
  if [ -z "$SMOKE_BAD" ] || [ -n "${V3_DRY:-}" ]; then block_end ok "smoke ${SMOKE_BAD:-all components ok}"; exit 0; fi
  block_end fail "smoke failed:$SMOKE_BAD"; exit 1
fi
rm -f "$OUT/marks.jsonl" "$OUT/heat.jsonl" "$OUT/order.json" "$OUT/idle.jsonl"   # left by an earlier attempt (V3_FORCE)
UNITS=$(unit_order)
printf '{"pass_arg":%s,"kind":"%s","pass":%s,"half":%s,"card":"%s","gov_free":%s,"heat_c":%s,"device":"%s","units":"%s"}\n' \
  "$ARG" "$KIND" "$K" "$HALF" "$CARD" "${GOV_FREE:-0}" "${HEAT_C:-null}" "${V3_DEVICE:-}" "$(echo $UNITS)" > "$OUT/order.json"
log "lat $KIND pass $K half $HALF: units $(echo $UNITS)"
for u in $UNITS; do "u_$u"; done
gzip -f "$OUT"/*/telemetry.jsonl "$OUT"/*/brackets.jsonl "$OUT"/*/*.err "$OUT"/*/stderr.log 2>/dev/null
block_end ok "units $(echo $UNITS)${NOTES:+; ${NOTES[*]}}"
