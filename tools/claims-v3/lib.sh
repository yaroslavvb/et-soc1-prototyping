# Shared helpers for the version-3 claim experiments (docs/reports/data/2026-09-25-claims-v3/PLAN3.md).
# Source it from a block script:  . "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
# It works unchanged on aifoundry2 (this repository) and aifoundry3 (~/nekko, a copy of it): the block scripts sit
# at tools/claims-v3/<exp>/ in both trees, and every path below is relative to the tree's root.
#
# Rules it enforces (CLAUDE.md, the lab's etiquette, and the traps in docs/findings/14-card-behaviour.md):
#  - no block starts while another user is logged in or another process holds the card (others_present);
#  - every device process goes through hold10, which caps it at 10 s (timeout 10);
#  - the sampler is stopped with SIGTERM only (a sampler killed mid-request poisons the management queue), and a
#    failed start is followed by one drain of the queue;
#  - on aifoundry2, power and latency blocks start on a warm die (heat_to), because below ~68 C its governor lifts
#    the clock off 600 MHz; aifoundry3 is pinned at 600 MHz and needs no heater.
set -u
V3_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$V3_ROOT"
export LD_LIBRARY_PATH=/opt/et/lib
# aifoundry3 has no system numpy: a user-level virtual environment in the tree (numpy 1.26.4, as on aifoundry2);
# aifoundry1 has no venv module either: the same numpy unpacked in pylib/
[ -x "$V3_ROOT/.venv/bin/python3" ] && export PATH="$V3_ROOT/.venv/bin:$PATH"
[ -d "$V3_ROOT/pylib/numpy" ] && export PYTHONPATH="$V3_ROOT/pylib${PYTHONPATH:+:$PYTHONPATH}"
CARD=$(hostname)                      # aifoundry2 | aifoundry3 | aifoundry1-c0 | aifoundry1-c1
# A host with several cards (aifoundry1 has two): V3_DEVICE=<n> selects card n. The host's deviceLayer honours
# ET_DEVICES (it then opens only that card, which the program sees as device 0), so every tool, the sampler included,
# works on the selected card; the card is named <host>-c<n> and has its own data directory.
if [ -n "${V3_DEVICE:-}" ]; then export ET_DEVICES=$V3_DEVICE; CARD="$CARD-c$V3_DEVICE"; fi
case "$CARD" in aifoundry2|aifoundry3|aifoundry1-c0|aifoundry1-c1) ;;
  aifoundry1) echo "aifoundry1 has two cards: set V3_DEVICE=0 or 1" >&2; exit 2 ;;
  *) echo "unknown card $CARD" >&2; exit 2 ;; esac
# Cards whose governor is free to move the clock (it lifts it off 600 MHz on a cool die): heat before power work and
# drop anything off 600 MHz. aifoundry3 is pinned at 600 MHz by a boot-time service (et-board-clock-guard).
case "$CARD" in aifoundry3) GOV_FREE= ;; *) GOV_FREE=1 ;; esac
ETTELEM=build/ettelem/ettelem
DEVMNGT=/opt/et/bin/dev_mngt_service
# Binaries: the same sources built on each host against its own /opt/et.
if [ "$CARD" = aifoundry2 ]; then
  MEMPROBE=build/memprobe-v3/host/memprobe_host   # a fresh build; build/memprobe is the 19 Sep one
  MMBENCH_DIR=$HOME/nekko                         # gp-sdk tree (deploy-lab-gpsdk.sh), outside this repository
  HEATER=build/sparsity_t2/host/sparsity_host
else
  MEMPROBE=build/memprobe/host/memprobe_host      # aifoundry3 and aifoundry1 (~/nekko trees)
  MMBENCH_DIR=$HOME/nekko
  HEATER=build/sparsity/host/sparsity_host
fi
ENERCAT=build/enercat/host/enercat_host
ENERCAT2=build/enercat_v2/host/enercat_host
MEMHIER=build/memhier/host/memhier_host
NOCBENCH=build/nocbench/host/nocbench_host
ONCHIP=build/onchip/host/onchip_host
SPARSITY=build/sparsity/host/sparsity_host
SGEMM=build/sgemm/host/sgemm_host
DATA_ROOT=$V3_ROOT/build/claims-v3/$CARD   # raw data; collected into docs/reports/data/2026-09-25-claims-v3-<card>/

log() { echo "$(date +%FT%T) [$CARD] $*"; }
now_ms() { date +%s%3N; }

# Device processes are recognised by executable name (ps comm, 15 characters), never by command line, so a shell
# whose command text mentions a host binary does not count.
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$'
# Other users' work also includes a running CI job (aifoundry1's GitHub Actions runner runs benchmarks as root).
OTHER_COMM="$DEV_COMM|^Runner.Worker$"
# Another user logged in, or a device process of another user running: the block must not start.
others_present() {
  local users procs holders
  users=$(who | awk '{print $1}' | sort -u | grep -vx "$USER" | tr '\n' ' ' || true)
  # A host with several cards (aifoundry1, amendment A3): another user who is only logged in does not block, since a
  # user there has kept an idle session open for days; what blocks is using the cards: a device node held by another
  # user (et-who sees every user's open nodes), another user's device process, or a running CI job (below).
  if [ -n "${V3_DEVICE:-}" ]; then
    users=
    if [ -x /usr/local/sbin/et-holders ]; then
      # fd 9 (our card lock) is closed for the call, or the helper's own sudo would show up as a root lock holder
      holders=$(sudo -n /usr/local/sbin/et-holders 9>&- 8>&- 2>/dev/null | grep -v 'et-holders' |
                awk -v me="$USER" '$1 ~ /^\/dev\/et|^lock:/ && $2 != me && $2 != "" {print $2":"$3}' | tr '\n' ' ')
      [ -n "${holders// /}" ] && users="holders:$holders"
    fi
  fi
  procs=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {print $1":"$2":"$3}' | tr '\n' ' ')
  if [ -n "${users// /}${procs// /}" ]; then log "others present: users=[$users] procs=[$procs]"; return 0; fi
  return 1
}
# Our own device processes still running (a previous block that did not clean up).
# With V3_DEVICE set, only our processes on the same card count (or with no ET_DEVICES, which open every card), so
# the two cards of one host can each run their own queue.
ours_running() {
  local pid e
  for pid in $(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {print $2}'); do
    [ -z "${V3_DEVICE:-}" ] && return 0
    e=$(tr '\0' '\n' < /proc/$pid/environ 2>/dev/null | grep '^ET_DEVICES=' || true)
    if [ -z "$e" ] || [ "$e" = "ET_DEVICES=$V3_DEVICE" ]; then return 0; fi
  done
  return 1
}
wait_free() {  # wait (up to $1 s, default 3600) until no other user and none of our device processes run
  local lim=${1:-3600} t=0
  while others_present || ours_running; do sleep 30; t=$((t + 30)); [ $t -ge "$lim" ] && return 1; done
  return 0
}

# Every device launch: at most 10 s on the card. Usage: hold10 <cmd> [args...]
hold10() { timeout 10 "$@" < /dev/null; }

# The die temperature (minion-shire mean, whole degrees) from a 1 s sample; empty if the sampler could not start.
die_c() { timeout 20 "$ETTELEM" sample --seconds 1 --every-ms 500 2>/dev/null | grep '^{' | tail -1 |
          sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p'; }
clock_mhz() { timeout 20 "$ETTELEM" sample --seconds 1 --every-ms 500 2>/dev/null | grep '^{' | tail -1 |
              sed -n 's/.*"minion":\([0-9]*\).*/\1/p'; }

# aifoundry2 only: heat the die to >= $1 C (default 76) with 2 s random-fp32 matmul launches; records the curve.
heat_to() {
  local target=${1:-76} out=${2:-/dev/null} t i
  [ -n "$GOV_FREE" ] || return 0
  local empty=0
  for i in $(seq 1 150); do
    t=$(die_c); echo "{\"t_ms\":$(now_ms),\"die_c\":${t:-0}}" >> "$out"
    if [ -z "$t" ]; then           # the management node does not answer: drain once, then give up; never heat blind
      empty=$((empty + 1)); [ $empty -eq 2 ] && drain_mgmt
      [ $empty -ge 4 ] && { log "heat_to: no die temperature after a drain; giving up"; return 1; }
      sleep 2; continue
    fi
    empty=0
    [ "$t" -ge "$target" ] && return 0
    hold10 "$HEATER" --test fma --type fp32 --pattern none --values randn \
      --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1 > /dev/null 2>&1
  done
  log "heat_to $target: gave up at ${t:-?} C"; return 1
}

# Drain a stale reply from the management queue (a sampler killed mid-request leaves one). /opt/et/bin/dev_mngt_service
# opens EVERY card's management node whatever -n says (it is the stock build, without ET_DEVICES), so on a host with
# several cards it runs only while no other card's block holds that card's lock; otherwise the drain is deferred.
drain_mgmt() {
  if [ -n "${V3_DEVICE:-}" ]; then
    local lk
    for lk in /run/lock/etsoc-shire*.lock; do
      [ "$lk" = "/run/lock/etsoc-shire$V3_DEVICE.lock" ] && continue
      exec 8<>"$lk"
      if ! flock -n 8; then exec 8>&-; log "drain deferred: another card's block holds $lk"; return 0; fi
    done
    timeout 20 "$DEVMNGT" -m DM_CMD_GET_MODULE_POWER -n "$V3_DEVICE" -u 5000 > /dev/null 2>&1 || true
    exec 8>&- 2>/dev/null
    return 0
  fi
  timeout 20 "$DEVMNGT" -m DM_CMD_GET_MODULE_POWER -n 0 -u 5000 > /dev/null 2>&1 || true
}

# Start the 10 Hz sampler into $1 (JSON lines) for at most $2 s (extra ettelem args after); sets SAMPLER_PID.
# Waits for its first line and retries (about one start in three fails right after a previous instance).
# While it runs nothing else may open the management node (die_c, clock_mhz, heat_to, dev_mngt_service).
SAMPLER_PID=; SAMPLER_OUT=
start_sampler() {
  local out=$1 secs=$2; shift 2
  local attempt i
  for attempt in 1 2 3 4 5 6; do
    "$ETTELEM" sample --seconds "$secs" --every-ms 100 "$@" > "$out.raw" 2>/dev/null < /dev/null &
    SAMPLER_PID=$!; SAMPLER_OUT=$out
    for i in $(seq 1 40); do sleep 0.25; grep -q '^{' "$out.raw" 2>/dev/null && return 0; done
    stop_sampler
    [ "$attempt" = 2 ] && drain_mgmt
    sleep 2
  done
  log "sampler failed to start"; return 1
}
# SIGTERM only: ettelem finishes its current request and exits (a SIGKILL mid-request leaves a reply queued).
stop_sampler() {
  [ -n "${SAMPLER_PID:-}" ] || return 0
  kill -TERM "$SAMPLER_PID" 2>/dev/null
  local i; for i in $(seq 1 300); do kill -0 "$SAMPLER_PID" 2>/dev/null || break; sleep 0.1; done
  if kill -0 "$SAMPLER_PID" 2>/dev/null; then
    # 30 s after SIGTERM it is stuck inside a request: the queue is already blocked, so kill it and drain the reply
    log "sampler $SAMPLER_PID ignored SIGTERM for 30 s: SIGKILL and drain"
    kill -KILL "$SAMPLER_PID" 2>/dev/null; sleep 1; drain_mgmt
  fi
  wait "$SAMPLER_PID" 2>/dev/null
  grep '^{' "$SAMPLER_OUT.raw" >> "$SAMPLER_OUT" 2>/dev/null; rm -f "$SAMPLER_OUT.raw"
  SAMPLER_PID=; SAMPLER_OUT=
}

# Block bookkeeping: block_begin <exp> <pass> creates $OUT and writes block.json when the block ends.
block_begin() {
  EXP=$1; PASS=$2; OUT=$DATA_ROOT/$EXP/p$PASS
  if [ -e "$OUT/block.json" ] && [ -z "${V3_FORCE:-}" ]; then log "$EXP p$PASS already done"; exit 0; fi
  # the machine's advisory card lock (labfix, 25 Sep): CI jobs and other tools take it too; held until the block exits
  local lk=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
  if [ -e "$lk" ] && [ -z "${V3_DRY:-}" ]; then
    exec 9<>"$lk"; flock -n 9 || { log "card lock $lk is held by another process: not starting"; exit 3; }
  fi
  mkdir -p "$OUT"; BLOCK_T0=$(now_ms)
  BLOCK_C0=$(die_c)
  sha256sum tools/claims-v3/lib.sh tools/claims-v3/"$EXP"/* > "$OUT/code.sha256" 2>/dev/null || true
  trap 'stop_sampler' EXIT
  log "$EXP p$PASS begins (die ${BLOCK_C0:-?} C) -> $OUT"
}
block_end() {  # block_end <status> [note]
  local st=$1 note=${2:-} c1
  stop_sampler
  c1=$(die_c || true)
  printf '{"exp":"%s","pass":%s,"card":"%s","t0_ms":%s,"t1_ms":%s,"die_c_start":%s,"die_c_end":%s,"status":"%s","note":"%s"}\n' \
    "$EXP" "$PASS" "$CARD" "$BLOCK_T0" "$(now_ms)" "${BLOCK_C0:-null}" "${c1:-null}" "$st" "${note//\"/\'}" > "$OUT/block.json"
  log "$EXP p$PASS ends: $st $note"
}

# V3_DRY=1: no device access at all. Device calls print what they would run, the die reads 80 C, data goes to
# build/claims-v3-dry/. For checking a block's logic off the card: V3_DRY=1 bash tools/claims-v3/<exp>/block.sh 1
if [ -n "${V3_DRY:-}" ]; then
  DATA_ROOT=$V3_ROOT/build/claims-v3-dry/$CARD
  hold10() { echo "DRY hold10: $*" >&2; }
  die_c() { echo 80; }
  clock_mhz() { echo 600; }
  heat_to() { echo "DRY heat_to ${1:-76}" >&2; }
  drain_mgmt() { echo "DRY drain_mgmt" >&2; }
  start_sampler() { echo "DRY start_sampler $*" >&2; SAMPLER_PID=; SAMPLER_OUT=$1; : > "$1"; }
  stop_sampler() { SAMPLER_PID=; }
  others_present() { return 1; }
  ours_running() { return 1; }
fi
