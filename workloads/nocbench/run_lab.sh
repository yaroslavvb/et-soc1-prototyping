#!/usr/bin/env bash
# The latency, size and collective probes behind the report, run on a lab machine:
#   ssh aifoundry2 'cd ~/nekko && bash workloads/nocbench/run_lab.sh build/nocbench/host/nocbench_host OUTDIR [GROUP...]'
# Groups: classes counts stream functs matrix sync allreduce barrier xallreduce (default: all, in that order).
# Each command is its own `timeout 10` process with --budget 8, and the script waits for the card to be
# free (no other process holding the et_soc1 driver) before each one, with a pause in between.
# A background loop logs board power and the minion clock (OUTDIR/clock.csv) from the service processor,
# because the DVFS governor moves the clock between runs: cross-shire latency is fixed in ns, not cycles.
set -uo pipefail
bin=${1:?usage: $0 <nocbench_host> <outdir> [group...]}
out=${2:?usage: $0 <nocbench_host> <outdir> [group...]}
shift 2
groups=("$@")
[[ ${#groups[@]} -gt 0 ]] || groups=(classes counts stream functs matrix sync allreduce barrier xallreduce)
mkdir -p "$out"

# Minion 0.0 to: its neighbourhood, where 0-1, 0-2 and 0-4 are fast-local-network pairs and 0-3, 0-5, 0-6,
# 0-7 and 1-2 are not (core-et Neighborhood MAS 4.7); the other three neighbourhoods of shire 0; and other
# shires 1, 3, 7 and 10 mesh hops away (marty1885's layout).
CLASSES=0.0-0.1,0.0-0.2,0.0-0.4,0.0-0.3,0.0-0.5,0.0-0.6,0.0-0.7,0.1-0.2,0.0-0.8,0.0-0.16,0.0-0.24,0.0-0.31,0.0-8.0,0.0-24.0,0.0-1.0,0.0-5.0,0.0-31.0
SHORT=0.0-0.1,0.0-0.7,0.0-8.0,0.0-31.0

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
  grep -c '"ok":true' "$out/$name.jsonl" | sed 's/^/   ok lines: /'
  grep '"ok":false' "$out/$name.jsonl" | head -3
  [[ $rc -eq 0 ]] || { echo "   exit $rc"; tail -5 "$out/$name.err"; }
  sleep 3
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
  classes)
    run classes-pingpong --test pairs --pairs $CLASSES --counts 1 --iters 4000 --warmup 100
    run classes-fcc --test pairs --mode fcc --pairs $CLASSES --iters 4000 --warmup 100
    run classes-flag --test pairs --mode flag --pairs $CLASSES --iters 2000 --warmup 50
    ;;
  counts)
    run counts-pingpong --test pairs --pairs $SHORT --counts 1,2,4,8,16,24,32,48,64,96,127 --iters 2000 --warmup 50
    ;;
  stream)
    run counts-stream --test pairs --mode stream --pairs $SHORT --counts 1,2,4,8,16,24,32,48,64,96,127 --iters 4000 --warmup 50
    ;;
  functs)
    for f in iadd imax fadd fmax; do
      run "functs-$f" --test pairs --pairs 0.0-0.1,0.0-8.0 --counts 1,32 --funct $f --iters 2000 --warmup 50
    done
    ;;
  matrix)
    run matrix-pingpong --test matrix --iters 300 --warmup 20
    run matrix-pingpong-m31 --test matrix --minion 31 --iters 300 --warmup 20
    run matrix-pingpong-c32 --test matrix --count 32 --iters 300 --warmup 20
    run intra-pingpong --test intra --shire 0 --iters 300 --warmup 20
    run intra-pingpong-s24 --test intra --shire 24 --iters 300 --warmup 20
    ;;
  sync)
    # Credits inside one shire, with the blocking FCC wait (the default there) and with polling.
    run fcc-inshire-block --test pairs --mode fcc --pairs 0.0-0.1,0.0-0.7,0.0-0.8,0.0-0.31 --iters 4000 --warmup 100
    run fcc-inshire-poll --test pairs --mode fcc --pairs 0.0-0.1,0.0-0.7,0.0-0.8,0.0-0.31 --iters 4000 --warmup 100 --poll 1
    run matrix-fcc --test matrix --mode fcc --iters 300 --warmup 20
    run matrix-flag --test matrix --mode flag --iters 200 --warmup 10
    ;;
  allreduce)
    # Levels 1-5: one tree per shire, alone (shire 0) and all 32 shires at once.
    for c in 1 8 32; do
      run "allreduce-c$c" --test allreduce --count $c --iters 1000 --shires 0x1
      run "allreduce-all-c$c" --test allreduce --count $c --iters 1000
    done
    ;;
  xallreduce)
    # Levels 6-10: trees across 2 to 32 shires (1024 minions).
    for c in 1 32; do
      run "xallreduce-c$c" --test allreduce --levels 6,7,8,9,10 --count $c --iters 500
    done
    ;;
  barrier)
    run barrier-shire1 --test barrier --scope shire --shires 0x1 --iters 4000 --warmup 100
    run barrier-shire32 --test barrier --scope shire --iters 4000 --warmup 100
    run barrier-chip1 --test barrier --scope chip --per-shire 1 --iters 2000 --warmup 50
    run barrier-chip32 --test barrier --scope chip --iters 2000 --warmup 50
    ;;
  *)
    echo "unknown group $g" >&2
    exit 2
    ;;
  esac
done
echo "done: $out"
