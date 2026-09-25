#!/usr/bin/env bash
# The cycle-count sweeps behind the sparsity report, run on a lab machine:
#   ssh aifoundry3 'cd ~/nekko && bash workloads/sparsity/run_lab.sh build/sparsity/host/sparsity_host OUTDIR [GROUP...]'
# Groups: fma tload gemv diverge (default: all, in that order).
# Each command is its own `timeout 10` process with --budget 8. Before each one the script waits until no other
# process holds the card, and it pauses between runs. A background loop logs the minion clock and board power
# (OUTDIR/clock.csv), because the DVFS governor can move the clock (600, 700 or 800 MHz on aifoundry2; aifoundry3
# stays at 600).
set -uo pipefail
bin=${1:?usage: $0 <sparsity_host> <outdir> [group...]}
out=${2:?usage: $0 <sparsity_host> <outdir> [group...]}
shift 2
groups=("$@")
[[ ${#groups[@]} -gt 0 ]] || groups=(fma tload gemv diverge)
mkdir -p "$out"

SWEEP=0,0.125,0.25,0.375,0.5,0.625,0.75,0.875,0.9375,1
ONE="--shires 0x1 --per-shire 1"           # one minion: cycle counts without contention
ALL="--shires 0xFFFFFFFF --per-shire 32"   # all 1024 compute minions

wait_free() {
  for _ in $(seq 60); do
    # Driver references minus this script's own clock queries (dev_mngt_service opens the device briefly).
    local refs ours
    refs=$(awk '$1 == "et_soc1" {print $3}' /proc/modules)
    ours=$(pgrep -u "$(id -u)" -c -f dev_mngt_service)
    if (( refs - ours <= 0 )) && ! pgrep -x et-powertop > /dev/null; then
      return 0
    fi
    sleep 2
  done
  echo "card still busy after 120 s, giving up" >&2
  exit 1
}

run() {  # run NAME ARGS...: one process, output in OUTDIR/NAME.jsonl
  local name=$1
  shift
  wait_free
  echo "== $name: $*"
  timeout 10 "$bin" --budget 8 "$@" > "$out/$name.jsonl" 2> "$out/$name.err"
  local rc=$?
  echo "   ok lines: $(grep -c '"ok":true' "$out/$name.jsonl"), failed: $(grep -c '"ok":false' "$out/$name.jsonl")"
  grep '"ok":false' "$out/$name.jsonl" | head -2
  [[ $rc -eq 0 ]] || { echo "   exit $rc"; grep -v '^I20' "$out/$name.err" | tail -4; }
  sleep 2
}

DMS=${ET:-/opt/et}/bin/dev_mngt_service
(
  echo "epoch_ms,minion_mhz,watts"
  while :; do
    t=$(date +%s%3N)
    f=$("$DMS" -m DM_CMD_GET_ASIC_FREQUENCIES -n 0 -u 2000 2>&1 | grep -o 'Minion Shire: [0-9]*' | grep -o '[0-9]*$')
    w=$("$DMS" -m DM_CMD_GET_MODULE_POWER -n 0 -u 2000 2>&1 | grep -o 'Module Power Output: [0-9.]*' | grep -o '[0-9.]*$')
    echo "$t,$f,$w"
    sleep 0.2
  done
) >> "$out/clock.csv" &
logger=$!
trap 'kill $logger 2>/dev/null' EXIT

for g in "${groups[@]}"; do
  case $g in
  fma)
    for p in elem col row; do
      run "fma-fp32-$p" --test fma --type fp32 --pattern $p --sweep $SWEEP $ONE
    done
    run fma-fp32-elem-tenb --test fma --type fp32 --pattern elem --sweep $SWEEP --b-stream $ONE
    run fma-fp32-bsparse --test fma --type fp32 --pattern none --sweep 0 --b-sparsity 0.5 $ONE
    run fma-fp32-bsparse90 --test fma --type fp32 --pattern none --sweep 0 --b-sparsity 0.9 $ONE
    for m in 0xFFFF 0x00FF 0x000F 0x0001 0x0000; do
      run "fma-fp32-rowmask-$m" --test fma --type fp32 --pattern none --sweep 0 --row-mask $m $ONE
    done
    run fma-fp16-elem --test fma --type fp16 --pattern elem --sweep $SWEEP $ONE
    run fma-fp16-pair --test fma --type fp16 --pattern pair --sweep 0,0.5,1 $ONE
    run fma-int8-elem --test fma --type int8 --pattern elem --sweep $SWEEP $ONE
    run fma-fp32-elem-all --test fma --type fp32 --pattern elem --sweep 0,0.5,0.875,1 $ALL --iters 4000
    ;;
  tload)
    for w in dram l2 scp; do
      run "tload-$w-one" --test tload --where $w --masks 0xFFFF,0x7FFF,0xFF,0xF,0x3,0x1,0x0 $ONE --iters 20000
      run "tload-$w-all" --test tload --where $w --masks 0xFFFF,0xFF,0xF,0x1,0x0 $ALL --iters 2000
    done
    ;;
  gemv)
    run gemv-dense --test gemv --gemv dense --sweep 0,0.5,0.75,0.9,0.95,0.99,1 $ALL --iters 2000
    run gemv-masked --test gemv --gemv masked --sweep 0,0.5,0.75,0.9,0.95,0.99,1 $ALL --iters 2000
    run gemv-skip --test gemv --gemv skip --sweep 0,0.5,0.75,0.9,0.95,0.99,1 $ALL --iters 2000
    run gemv-skip-oneshire --test gemv --gemv skip --sweep 0,0.9,0.99 --shires 0x1 --per-shire 32 --iters 2000
    for g in dense masked skip; do  # the same layer, summed on chip with TensorReduce
      run "gemv-tree-$g" --test gemv --gemv $g --gemv-tree --sweep 0,0.5,0.75,0.9,0.95,0.99,1 $ALL --iters 2000
    done
    run gemv-tree-oneshire --test gemv --gemv skip --gemv-tree --sweep 0,0.9,0.99 --shires 0x1 --per-shire 32 --iters 2000
    ;;
  diverge)
    for a in 0 3 2 1.5 1.2; do
      for v in static refill scalar; do
        run "diverge-$v-a$a" --test diverge --variant $v --alpha $a --mean-k 64 --kmax 16384 --items 256 --harts 2 $ALL
      done
    done
    ;;
  *)
    echo "unknown group $g" >&2
    exit 2
    ;;
  esac
done
echo "done: $out"
