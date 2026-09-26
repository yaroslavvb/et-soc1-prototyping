# Patched run_ablation.sh for the version-3 blocks abla, ablb and x5 (PLAN3 §3 N3), as functions.
# Source it after ../lib.sh:   . "$V3_ROOT/tools/claims-v3/abla/ablrun.sh"
#
# It is tools/ettelem/run_ablation.sh with the plan's patches, adapted to the block framework:
#  - it works from the tree root ($V3_ROOT, set by lib.sh), never from its own location;
#  - every device launch (runs and heater bursts) goes through hold10 (timeout 10, was timeout secs+5);
#  - the 10 Hz sampler is lib.sh's start_sampler/stop_sampler (SIGTERM, retry + drain), not a bare background
#    ettelem that the original killed with kill on EXIT;
#  - @TSEED@ becomes (block % 2) + 1 (committed structured-tile seeds 1 and 2 only); @SEED@ and --seed take
#    block + 1 + SEED_OFFSET (SEED_OFFSET 0 unless given);
#  - before the sampler starts, the et_soc1 use count must be 0; the count with only our sampler open is then
#    measured (ABL_NS, the plan's "1"). Before each run it waits while anyone else holds the card (use count > ABL_NS,
#    or another user's device process or a CI job: lib.sh's OTHER_COMM), at most ABL_WAIT_MAX_S (900 s), else the
#    session stops with code 3; the check is repeated before every heater burst and after the approach, and a card
#    taken during the approach means wait and approach again (no burst is fired while someone else holds the card);
#  - on a host with several cards (V3_DEVICE set: aifoundry1) the et_soc1 use count counts every card, and the other
#    card's queue holds its own card, so the count is not used: "someone else holds the card" is then another user's
#    device process or CI job (the process half of lib.sh's others_present) or one of our own device processes that
#    can open this card (lib.sh's ours_running rule: ET_DEVICES unset or this card; a dev_mngt_service always, as it
#    ignores ET_DEVICES and opens every card), other than this session's sampler;
#  - the approach stops (code 2) when the sampler's lines carry no die temperature, instead of heating blind;
#  - one session is ONE block (the framework's pass) with the block index given, so the shuffle of a pass is the
#    one the original's one-invocation loop gave that block: random.Random(block + 11);
#  - safety stops the original lacked: sampler dead or stale (> 5 s) -> code 2; session longer than ABL_CAP_S
#    -> code 4; each run's host exit code goes to ends.jsonl; host stderr to host.log;
#  - starts.jsonl lines carry heats (heater launches of that approach), preheat_reached, seed, waited_ms, and the
#    idle operating point just before the launch (idle_mhz, idle_mv from the sampler's last complete line): a card
#    whose firmware idles in a low-power state (aifoundry1 card 0: 300 MHz / 398 mV) shows it there;
#  - every card runs the approach with its block's temperatures (blocks choose them by GOV_FREE, not by host name).
# The approach itself is the original's: up to 60 heater bursts (2 s fp32 randn on 1,024 minions) until the
# minion-shire mean reads >= preheat, then idle (0.2 s polls, at most 600 s) until it reads <= target.
# V3_DRY=1: the die temperature is simulated (a burst adds 3 C, a poll removes 1 C) and sleeps are skipped.

cd "$V3_ROOT" || exit 2
ABL_LIB=$V3_ROOT/tools/claims-v3/abla
ABL_HOST=${ABL_HOST:-$SPARSITY}
ABL_WAIT_MAX_S=${ABL_WAIT_MAX_S:-900}
ABL_DRY_T=0

nap() { [ -n "${V3_DRY:-}" ] || sleep "$1"; }

# Record what ran: hashes of the shared runner, the experiment's own files, the host binary and its source.
abl_hash_code() {  # abl_hash_code <exp-dir-name> [extra files...]   (paths relative to the tree root)
  local d=$1 f; shift
  for f in tools/claims-v3/abla/ablrun.sh tools/claims-v3/abla/ablcore.py tools/claims-v3/abla/ablcheck.py \
           tools/claims-v3/"$d"/* "$ABL_HOST" workloads/sparsity/host/main.cpp workloads/sparsity/sparsity_args.h "$@"; do
    grep -q "  $f\$" "$OUT/code.sha256" 2>/dev/null || sha256sum "$f" >> "$OUT/code.sha256" 2>/dev/null
  done
  return 0
}

# The structured tiles that abl_a.cfg reads must be the committed ones (aifoundry3, aifoundry1: rsynced copies).
abl_check_tiles() {
  sha256sum --quiet -c "$ABL_LIB/tiles.sha256" > "$OUT/tiles.check" 2>&1 && return 0
  log "structured tiles missing or different: $(tr '\n' ' ' < "$OUT/tiles.check")"; return 1
}

abl_use_count() { awk '$1=="et_soc1"{print $3; f=1} END{if(!f) print 0}' /proc/modules 2>/dev/null; }
abl_foreign_dev() {  # another user's device process or CI job (the same test as lib.sh's others_present, processes only)
  ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="${OTHER_COMM:-$DEV_COMM}" '$1 != me && $3 ~ re {f=1} END {exit !f}'
}
# V3_DEVICE set: one of our own device processes that can open this card (ET_DEVICES unset: every card; or this
# card), other than this session's sampler: lib.sh's ours_running rule, which would otherwise count our sampler.
# /opt/et/bin/dev_mngt_service ignores ET_DEVICES and opens every card (lessons, 25 Sep), so one from the other card's
# queue (lib.sh's drain_mgmt) counts whatever its ET_DEVICES says.
abl_ours_other() {
  local pid e c
  while read -r pid c; do
    [ "$pid" = "${SAMPLER_PID:-}" ] && continue
    [ -r "/proc/$pid/environ" ] || continue          # exited since ps listed it
    case $c in dev_mngt_servi*) return 0 ;; esac
    e=$(tr '\0' '\n' < "/proc/$pid/environ" 2>/dev/null | grep '^ET_DEVICES=' || true)
    if [ -z "$e" ] || [ "$e" = "ET_DEVICES=$V3_DEVICE" ]; then return 0; fi
  done < <(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {print $2, $3}')
  return 1
}
# The card is held by someone else. With V3_DEVICE: processes only (see above); otherwise the use count must be
# <= $1 and no other user's device process may run.
abl_held() {
  if [ -n "${V3_DEVICE:-}" ]; then abl_foreign_dev || abl_ours_other; return; fi
  local n; n=$(abl_use_count)
  [ "${n:-0}" -gt "$1" ] || abl_foreign_dev
}
# ABL_NS: the et_soc1 use count with only our sampler open (the plan's "1"; measured after the sampler starts, so a
# sampler that holds more than one handle does not make every run wait for ever). Set by abl_session.
ABL_NS=1
# Wait (at most ABL_WAIT_MAX_S) while the card is held by someone else; sets ABL_WAITED_MS.
# abl_wait_card [limit]: the use count must be <= limit (default ABL_NS; 0 before our sampler starts).
abl_wait_card() {
  ABL_WAITED_MS=0
  [ -n "${V3_DRY:-}" ] && return 0
  local t0 logged= lim=${1:-$ABL_NS}
  t0=$(now_ms)
  while :; do
    if ! abl_held "$lim"; then ABL_WAITED_MS=$(( $(now_ms) - t0 )); [ -n "$logged" ] && log "card free again"; return 0; fi
    [ -z "$logged" ] && { log "card held by someone else ($([ -n "${V3_DEVICE:-}" ] && echo "a device process that can open card $V3_DEVICE" || echo "et_soc1 use count $(abl_use_count), ours $lim")): waiting"; logged=1; }
    [ $(( $(now_ms) - t0 )) -ge $(( ABL_WAIT_MAX_S * 1000 )) ] && { log "still held after ${ABL_WAIT_MAX_S} s"; return 1; }
    sleep 5
  done
}

abl_card_free_now() {  # no waiting: nobody else holds the card at this moment
  [ -n "${V3_DRY:-}" ] && return 0
  ! abl_held "$ABL_NS"
}

# The sampler is alive and its last line is at most 5 s old.
abl_alive() {
  [ -n "${V3_DRY:-}" ] && return 0
  [ -n "${SAMPLER_PID:-}" ] && kill -0 "$SAMPLER_PID" 2>/dev/null || { log "sampler is not running"; return 1; }
  local ms
  ms=$(tail -n 3 "$SAMPLER_OUT.raw" 2>/dev/null | grep '^{' | tail -n 1 | sed -n 's/^{"t_ms":\([0-9]*\).*/\1/p')
  [ -n "$ms" ] && [ $(( $(now_ms) - ms )) -le 5000 ] && return 0
  log "sampler output is stale (last t_ms ${ms:-none})"; return 1
}
# The die temperature (minion-shire mean, whole degrees) from the sampler's second-to-last line, as the original.
abl_temp() {
  if [ -n "${V3_DRY:-}" ]; then echo "$ABL_DRY_T"; return; fi
  tail -n 3 "$SAMPLER_OUT.raw" 2>/dev/null | grep '^{' | tail -n 2 | head -n 1 | sed -n 's/.*"minshire":\[\([0-9]*\).*/\1/p'
}

# The idle operating point just before a launch: "<minion MHz> <minion mV>" from the sampler's second-to-last line
# ("null" for a field that is absent). V3_DRY: ABL_DRY_IDLE (default "600 516").
abl_clock() {
  if [ -n "${V3_DRY:-}" ]; then echo "${ABL_DRY_IDLE:-600 516}"; return; fi
  local ln mhz mv
  ln=$(tail -n 3 "$SAMPLER_OUT.raw" 2>/dev/null | grep '^{' | tail -n 2 | head -n 1)
  mhz=$(sed -n 's/.*"mhz":{"minion":\([0-9]*\).*/\1/p' <<< "$ln")
  mv=$(sed -n 's/.*"die_mv":{[^}]*"minion":\([0-9]*\).*/\1/p' <<< "$ln")
  echo "${mhz:-null} ${mv:-null}"
}

abl_heat_burst() {  # one 2 s heater launch (the original's approach() burst)
  hold10 "$ABL_HOST" --test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 \
    --seconds 2 --seed 1 2>&"$ABL_EFD" | grep SPARSITY | sed "s/^SPARSITY //; s/^{/{\"block\":-9,\"config\":\"preheat\",/" >> "$ABL_OUT/runs.jsonl"
  [ -n "${V3_DRY:-}" ] && ABL_DRY_T=$(( ABL_DRY_T + 3 ))
  return 0
}

# approach <target> <preheat>: 0 ready, 2 sampler lost (or no temperature in its lines), 5 someone else took the
# card between heater bursts (the caller waits and approaches again; no burst is fired onto another user's run).
# Sets ABL_HEATS, ABL_PREHEAT_OK.
abl_approach() {
  local target=$1 preheat=$2 i t notemp=0
  ABL_HEATS=0; ABL_PREHEAT_OK=false
  for i in $(seq 1 60); do
    abl_alive || return 2
    t=$(abl_temp)
    if [ -z "$t" ]; then  # the sampler runs but its lines carry no die temperature: never heat blind
      notemp=$(( notemp + 1 )); [ "$notemp" -ge 5 ] && { log "no die temperature in the sampler's lines"; return 2; }
      nap 0.5; continue
    fi
    notemp=0
    [ "$t" -ge "$preheat" ] && { ABL_PREHEAT_OK=true; break; }
    abl_card_free_now || return 5
    abl_heat_burst; ABL_HEATS=$(( ABL_HEATS + 1 ))
  done
  for i in $(seq 1 3000); do
    t=$(abl_temp); [ -n "$t" ] && [ "$t" -le "$target" ] && return 0
    if [ -n "${V3_DRY:-}" ]; then ABL_DRY_T=$(( ABL_DRY_T - 1 )); continue; fi
    [ $(( i % 25 )) -eq 0 ] && { abl_alive || return 2; }
    sleep 0.2
  done
  return 0  # as the original: after 600 s the run starts at whatever temperature the die has
}

# abl_session <out-dir> <cfg> <block> <seconds> <target_c> <preheat_c> [seed_offset]
# Returns 0 done, 2 sampler lost, 3 someone else held the card too long, 4 time cap (ABL_CAP_S) reached.
# ABL_NO_APPROACH=1 (smoke only): one heater burst at the start instead of an approach before every run.
abl_session() {
  local out=$1 cfg=$2 block=$3 secs=$4 target=$5 preheat=$6 so=${7:-0}
  local name args seed t_a t_run rc=0 hrc t0 cap=${ABL_CAP_S:-2700} tstart try waited arc imhz imv
  ABL_OUT=$out; mkdir -p "$out"
  # host stderr: host.log (V3_DRY: this shell's stderr, so the dry run shows every launch in order)
  if [ -n "${V3_DRY:-}" ]; then exec {ABL_EFD}>&2; ABL_DRY_T=$(( target - 3 )); else exec {ABL_EFD}>>"$out/host.log"; fi
  cp "$cfg" "$out/config.cfg"
  : > "$out/runs.jsonl"; : > "$out/starts.jsonl"; : > "$out/ends.jsonl"
  # Before our sampler opens the card nobody may hold it (use count 0); then measure what our sampler alone holds.
  # V3_DEVICE set (a host with several cards): no use count (it counts both cards), the process checks only.
  local n0=0 i n check=use_count
  [ -n "${V3_DEVICE:-}" ] && { check="processes (V3_DEVICE set: the et_soc1 use count counts every card of the host)"; n0=null; }
  [ -n "${V3_DRY:-}" ] || [ -n "${V3_DEVICE:-}" ] || n0=$(abl_use_count)
  abl_wait_card 0 || { exec {ABL_EFD}>&-; return 3; }
  t0=$(now_ms)
  # The sampler outlives the cap by 15 min, so the last run's approach (<= 60 bursts + 600 s idle) cannot outlast it;
  # it is stopped with SIGTERM when the session ends.
  start_sampler "$out/telemetry.jsonl" $(( cap + 900 )) || { exec {ABL_EFD}>&-; return 2; }
  ABL_NS=1
  if [ -z "${V3_DRY:-}" ] && [ -z "${V3_DEVICE:-}" ]; then
    for i in 1 2 3 4 5; do n=$(abl_use_count); [ -n "$n" ] && [ "$n" -gt "$ABL_NS" ] && ABL_NS=$n; sleep 0.2; done
    [ "$ABL_NS" -gt 1 ] && log "et_soc1 use count with only our sampler open: $ABL_NS (the plan expects 1); using it as the baseline"
  fi
  echo "{\"block\":$block,\"seconds\":$secs,\"target_c\":$target,\"preheat_c\":$preheat,\"seed_offset\":$so,\"host\":\"$ABL_HOST\",\"card\":\"$CARD\",\"device\":\"${V3_DEVICE:-}\",\"gov_free\":$([ -n "${GOV_FREE:-}" ] && echo true || echo false),\"cap_s\":$cap,\"card_check\":\"$check\",\"use_count_before\":${n0:-null},\"use_count_sampler\":$([ -n "${V3_DEVICE:-}" ] && echo null || echo $ABL_NS)}" > "$out/session.json"
  nap 3
  python3 -c "import random,sys; l=[x for x in open(sys.argv[2]).read().splitlines() if x.strip() and not x.startswith('#')]; random.Random(int(sys.argv[1])+11).shuffle(l); print('\n'.join(l))" "$block" "$cfg" > "$out/order.$block"
  [ -n "${ABL_NO_APPROACH:-}" ] && { abl_heat_burst; nap 1; }
  while read -r name args <&3; do
    if [ $(( $(now_ms) - t0 )) -gt $(( cap * 1000 )) ]; then log "time cap ${cap} s reached before $name"; rc=4; break; fi
    seed=$(( block + 1 + so ))
    args=${args//@SEED@/$seed}
    args=${args//@TSEED@/$(( block % 2 + 1 ))}
    t_a=$(now_ms)
    # wait for the card, approach, and launch only if nobody took the card during the approach (else wait and
    # approach again, at most 3 times)
    waited=0
    for try in 1 2 3 4; do
      [ "$try" = 4 ] && { log "the card was taken during three approaches"; rc=3; break 2; }
      abl_wait_card || { rc=3; break 2; }
      waited=$(( waited + ABL_WAITED_MS ))
      if [ -z "${ABL_NO_APPROACH:-}" ]; then
        abl_approach "$target" "$preheat"; arc=$?
        [ $arc -eq 2 ] && { rc=2; break 2; }
        [ $arc -eq 5 ] && { log "someone took the card between heater bursts before $name: waiting, then approaching again"; continue; }
      else
        ABL_HEATS=0; ABL_PREHEAT_OK=false
      fi
      abl_card_free_now && break
      log "someone took the card during the approach to $name: waiting, then approaching again"
    done
    tstart=$(abl_temp)
    read -r imhz imv <<< "$(abl_clock)"
    echo "{\"block\":$block,\"config\":\"$name\",\"start_temp\":${tstart:-null},\"approach_ms\":$(( $(now_ms) - t_a )),\"t_ms\":$(now_ms),\"heats\":$ABL_HEATS,\"preheat_reached\":$ABL_PREHEAT_OK,\"seed\":$seed,\"waited_ms\":$waited,\"tries\":$try,\"idle_mhz\":${imhz:-null},\"idle_mv\":${imv:-null}}" >> "$out/starts.jsonl"
    t_run=$(now_ms)
    # shellcheck disable=SC2086
    hold10 "$ABL_HOST" $args --seconds "$secs" --seed "$seed" 2>&"$ABL_EFD" | grep SPARSITY |
      sed "s/^SPARSITY //; s/^{/{\"block\":$block,\"config\":\"$name\",/" >> "$out/runs.jsonl"
    hrc=${PIPESTATUS[0]}
    echo "{\"block\":$block,\"config\":\"$name\",\"rc\":$hrc,\"t0_ms\":$t_run,\"t1_ms\":$(now_ms)}" >> "$out/ends.jsonl"
  done 3< "$out/order.$block"
  # the original's 20 s of idle after the last run (the reducers read no window there; kept for the telemetry tail),
  # skipped when someone else is waiting for the card
  [ $rc -eq 3 ] || nap 20
  stop_sampler
  exec {ABL_EFD}>&-
  [ -s "$out/telemetry.jsonl" ] || [ -n "${V3_DRY:-}" ] || { log "no telemetry recorded"; [ $rc -eq 0 ] && rc=2; }
  gzip -f "$out/telemetry.jsonl" 2>/dev/null
  return $rc
}
