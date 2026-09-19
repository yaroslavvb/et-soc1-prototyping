#!/usr/bin/env bash
# Every measurement behind docs/reports/2026-09-18-et-soc1-memory-hierarchy.html, run on a lab machine:
#   ssh aifoundry2 'cd ~/nekko && bash workloads/memhier/run_lab.sh build/memhier/host/memhier_host OUTDIR [GROUP...]'
# Groups: chase scp dvfs energy (default: all, in that order). The file names match
# docs/reports/data/2026-09-18-memhier-aifoundry2/, and workloads/memhier/analyze.py reads them from OUTDIR.
# Each command is its own `timeout 10` process (memhier_host stops launching after --budget 8), and the script
# waits for the card to be free before each one.
set -uo pipefail
bin=${1:?usage: $0 <memhier_host> <outdir> [group...]}
out=${2:?usage: $0 <memhier_host> <outdir> [group...]}
shift 2
groups=("$@")
[[ ${#groups[@]} -gt 0 ]] || groups=(chase scp dvfs energy)
mkdir -p "$out"
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DMS=${ET:-/opt/et}/bin/dev_mngt_service

wait_free() {
  for _ in $(seq 60); do
    local refs
    refs=$(awk '$1 == "et_soc1" {print $3}' /proc/modules)
    if [[ "$refs" == "0" ]] && ! pgrep -x et-powertop > /dev/null; then
      return 0
    fi
    sleep 2
  done
  echo "card still busy after 120 s, giving up" >&2
  exit 1
}

chase() {  # chase NAME ARGS...: one latency sweep, output in OUTDIR/NAME.jsonl
  local name=$1
  shift
  wait_free
  echo "== $name: $*"
  timeout 10 "$bin" --budget 8 --test chase "$@" > "$out/$name.jsonl" 2> "$out/$name.err"
  echo "   $(grep -c '"ok":true' "$out/$name.jsonl") ok, $(grep -c '"ok":false' "$out/$name.jsonl") failed"
  sleep 3
}

for g in "${groups[@]}"; do
  case $g in
  chase)
    chase chase-dram                                     # 256 B to 256 MB from shire 0
    chase chase-dram-sweep-from24 --chaser-shire 24
    chase chase-dram-thread1 --thread 1 --sizes 256,512,768,1K,4K
    for s in 7 24 31; do
      chase "chase-dram-from$s" --chaser-shire $s --sizes 4M,256M
    done
    chase chase-dram-from0-repeat --sizes 4M,256M
    # L3 (4 MB) and DRAM (256 MB) chains in fresh regions: how much DRAM latency depends on placement
    chase chase-dram-placement --steps 20000 --sizes 4M,4M,4M,4M,4M,4M,4M,4M,256M,4M,4M,4M,4M,256M
    chase chase-dram-offsets --steps 20000 --sizes 128M,128M,128M,128M,128M,128M,128M,128M
    ;;
  scp)
    chase chase-scp-local --where scp --scp-shire local --sizes 256,512,768,1K,2K,4K,8K,16K,64K,256K,1M,2M
    chase chase-scp-map --where scp --scp-shire all --sizes 64K
    for s in 7 24 31; do
      chase "chase-scp-map-from$s" --where scp --scp-shire all --sizes 64K --chaser-shire $s
    done
    ;;
  dvfs)
    # The service processor's clock, voltage and power every ~250 ms for 10 s, with a 2 s spin in the middle.
    wait_free
    echo "== dvfs-poll-during-spin"
    (
      t0=$(date +%s%3N)
      while (( $(date +%s%3N) - t0 < 10000 )); do
        t=$(( $(date +%s%3N) - t0 ))
        f=$("$DMS" -m DM_CMD_GET_ASIC_FREQUENCIES -n 0 -u 2000 2>&1 | grep -o 'Minion Shire: [0-9]*' | grep -o '[0-9]*$')
        v=$("$DMS" -m DM_CMD_GET_ASIC_VOLTAGE -n 0 -u 2000 2>&1 | grep -o 'Voltage MINION: [0-9]*' | grep -o '[0-9]*$')
        w=$("$DMS" -m DM_CMD_GET_MODULE_POWER -n 0 -u 2000 2>&1 | grep -o 'Module Power Output: [0-9.]*' | grep -o '[0-9.]*$')
        echo "$t ms f=$f MHz Vmin=$v mV P=$w W"
        sleep 0.1
      done
    ) > "$out/dvfs-poll-during-spin.txt" &
    poller=$!
    sleep 1.7
    timeout 10 "$bin" --budget 8 --test spin --seconds 2 > /dev/null 2>&1
    wait $poller
    sleep 3
    ;;
  energy)
    # Two independent runs, averaged by analyze.py (the report's energy table).
    for d in energy energy2; do
      wait_free
      python3 "$here/run_energy.py" --host-bin "$bin" --out "$out/$d"
      sleep 5
    done
    ;;
  *)
    echo "unknown group $g" >&2
    exit 2
    ;;
  esac
done
echo "done: $out"
