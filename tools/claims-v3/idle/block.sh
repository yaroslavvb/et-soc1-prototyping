#!/usr/bin/env bash
# V3-IDLE (PLAN3 §2 "V3-IDLE", suggested E44): ONE heat/cool cycle on the local card.
#
#   bash tools/claims-v3/idle/block.sh <pass> [--smoke]         (aifoundry1: V3_DEVICE=0|1 selects the card, lib.sh)
#
#   pass 1-9    a short cycle: heat, then 900 s with no launch            (items IDLE-0, a-f, k)
#   pass 11-19  an IDLE-LONG cycle: heat, then LONG_COOL_S with no launch (item IDLE-L; also a cycle for 0, a-f, k,
#               (5400 s aifoundry2 and aifoundry1's cards, 2700 s         using its first 900 s of cooling)
#               aifoundry3); overnight only, from a schedule of its own (one block of ~95 / ~60 min)
#   --smoke     the smallest real check of every component (~30 s of card time): sampler, live die reading from
#               the sampler, two heater bursts, 20 s idle with the intrusion poll, pass check by reduce.py
#
# Cards (lib.sh CARD): aifoundry2, aifoundry3, aifoundry1-c0, aifoundry1-c1. Per-card parameters (PLAN3; amendment A2
# for aifoundry1's cards, which take aifoundry2's values): heat target 88 C, IDLE-LONG cooling 5400 s, except aifoundry3
# (pinned at 600 MHz, faster heatsink): target 90 C, which it does not reach (it heats to its plateau), cooling 2700 s.
#
# One pass, in order:
#   1. nobody else on the card (lib others_present, lib ours_running for this card; the et_soc1 use count 0, except
#      with V3_DEVICE set: the module serves both cards of aifoundry1, whose other queue may hold its own card), else
#      exit 3 (the queue retries)
#   2. block_begin (die reading, card closed again), then the 10 Hz sampler for the whole cycle; the card's idle state
#      before heating (minion clock, minion voltage) from the sampler's first line goes into the cycle_start mark
#   3. heat: 2 s random-data fma bursts on all 1024 minions (lib HEATER; each under hold10) until the die reads
#      >= TARGET_C, at most 150 bursts or 900 s. The die is read from the running sampler's own output, never with a
#      second opener of the management node.
#   4. cool: no launch for COOL_S seconds; every 10 s check that the sampler is alive and that nobody opened the
#      card (scan_procs: a device process on this card other than our sampler, or the et_soc1 use count above the
#      sampler's own where it is checked); an intrusion stops the cycle (block_end fail, exit 3), because another
#      kernel spoils the idle samples. Our own processes on the other card of the host are counted, not an intrusion.
#   5. cool_end mark with the idle state at the end of the cooling; SIGTERM the sampler, gzip the telemetry, check the
#      pass (reduce.py --check-pass: the cooling window's clock histogram and idle clock), block_end.
# Files in $OUT: telemetry.jsonl.gz (10 Hz), launches.jsonl (every burst: t_start_ms, t_end_ms, rc), heat.jsonl
# (the die reading before every burst), marks.jsonl (cycle_start, heat_end, cool_start, cool_end, abort, login),
# cycle.json (the cycle's parameters), heater.out.gz (the heater's stdout), check.json, block.json.
set -u
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"     # cd's to the tree root; CARD, GOV_FREE, HEATER, ETTELEM, DATA_ROOT, helpers

PASS_ARG=${1:?usage: block.sh <pass> [--smoke]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
case "$PASS_ARG" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
PASS_ARG=$(( 10#$PASS_ARG ))     # "01" -> 1: the pass is written unquoted into cycle.json and block.json
HERE=tools/claims-v3/idle

# lib's block_end writes die_c's output unquoted into block.json, so a die reading that fails (ettelem does not
# start in about one try in three right after a previous instance) would leave invalid JSON ("die_c_end":,). This
# wrapper gives "null" instead. After an intrusion (NO_CARD=1) it does not open the card at all: the other user's
# process may be a sampler of its own, and the management node has one opener.
eval "lib_die_c() $(declare -f die_c | tail -n +2)"
die_c() { local t=; [ -n "${NO_CARD:-}" ] || t=$(lib_die_c); echo "${t:-null}"; }

# Per-card parameters: what the card is, not its name.
case "$CARD" in
  aifoundry3) TARGET_C=90; LONG_COOL_S=2700 ;;   # never reaches 90 C: heats to its plateau; its heatsink cools faster
  *)          TARGET_C=88; LONG_COOL_S=5400 ;;   # aifoundry2 (PLAN3); aifoundry1-c0/-c1 take aifoundry2's values (A2)
esac
if [ -n "$SMOKE" ]; then
  EXPNAME=idle-smoke; VARIANT=smoke; COOL_S=20; HEAT_MAX_BURSTS=2; HEAT_MAX_S=30
else
  EXPNAME=idle; HEAT_MAX_BURSTS=150; HEAT_MAX_S=900
  if [ "$PASS_ARG" -ge 1 ] && [ "$PASS_ARG" -le 9 ]; then VARIANT=short; COOL_S=900
  elif [ "$PASS_ARG" -ge 11 ] && [ "$PASS_ARG" -le 19 ]; then VARIANT=long; COOL_S=$LONG_COOL_S
  else echo "pass must be 1-9 (short cycle) or 11-19 (IDLE-LONG)" >&2; exit 2
  fi
fi
SAMPLER_S=$(( HEAT_MAX_S + COOL_S + 90 ))                              # outlives the cycle; stopped with SIGTERM
HEAT_ARGS=(--test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1)

dry() { [ -n "${V3_DRY:-}" ]; }
# et_soc1 module use count (who holds a card open). Reads /proc/modules only. The module serves every card of the host,
# so with V3_DEVICE set (aifoundry1: two cards, each with its own queue) the count includes the other card's holders:
# the check is skipped there (empty output), and the per-card process checks (lib ours_running, scan_procs) stand.
if [ -n "${V3_DEVICE:-}" ]; then MODCHECK=skipped; else MODCHECK=on; fi
modcount() {
  [ "$MODCHECK" = on ] || { echo; return 0; }
  if dry; then echo 0; else lsmod 2>/dev/null | awk '$1=="et_soc1"{print $3}'; fi
}
# ET_DEVICES of one of our own processes (empty if it has none); exit 1 if the process is gone.
penv_devices() {
  local env; env=$( { tr '\0' '\n' < "/proc/$1/environ"; } 2>/dev/null ) || return 1
  [ -n "$env" ] || [ -e "/proc/$1" ] || return 1
  sed -n 's/^ET_DEVICES=//p' <<< "$env" | head -n 1
}
# The device processes on the host other than our sampler, one line each:
#   F uid:pid:comm   on this card: another user's device process or CI job (lib OTHER_COMM), or one of ours with
#                    ET_DEVICES = V3_DEVICE or none (it opens every card); dev_mngt_service opens every card whatever
#                    its ET_DEVICES, so it is always on this card
#   O uid:pid:comm   one of ours on the other card of this host (ET_DEVICES set and not listing V3_DEVICE: its own queue)
# Without V3_DEVICE (aifoundry2, aifoundry3) every such process is F, as before. An ET_DEVICES list ("0,1") that names
# this card counts as on this card.
scan_procs() {
  dry && return 0
  local me uid pid comm e
  me=$(id -u)
  ps -eo uid=,pid=,comm= |
    awk -v me="$me" -v dev="$DEV_COMM" -v oth="$OTHER_COMM" -v sp="${SAMPLER_PID:-0}" \
      '$2 != sp && (($1 == me && $3 ~ dev) || ($1 != me && $3 ~ oth)) {print $1, $2, $3}' |
    while read -r uid pid comm; do
      if [ -n "${V3_DEVICE:-}" ] && [ "$uid" = "$me" ] && [ "$comm" != dev_mngt_servi ]; then
        e=$(penv_devices "$pid") || continue                     # gone since ps: not on the card any more
        if [ -n "$e" ]; then
          case ",${e// /,}," in *",$V3_DEVICE,"*) ;; *) echo "O $uid:$pid:$comm"; continue ;; esac
        fi
      fi
      echo "F $uid:$pid:$comm"
    done
}
foreign_procs() { scan_procs | awk '$1 == "F" {print $2}' | tr '\n' ' '; }
other_logins() { who | awk '{print $1}' | sort -u | grep -vx "$USER" | tr '\n' ' ' || true; }
mark() {  # mark <event> [extra JSON fields, already formatted: "\"k\":v,..."]
  local extra=${2:-}; [ -n "$extra" ] && extra=",$extra"
  echo "{\"t_ms\":$(now_ms),\"ev\":\"$1\"$extra}" >> "$OUT/marks.jsonl"
}
newest_line() { tail -n 4 "$SAMPLER_OUT.raw" 2>/dev/null | grep '^{.*}$' | tail -n 1; }
# The newest complete sampler line: "<age_ms> <die_c>"; non-zero if there is none.
live_reading() {
  local l t c
  l=$(newest_line)
  [ -n "$l" ] || return 1
  t=$(sed -n 's/^{"t_ms":\([0-9]*\),.*/\1/p' <<< "$l"); c=$(sed -n 's/.*"minshire":\[\([0-9]*\).*/\1/p' <<< "$l")
  [ -n "$t" ] && [ -n "$c" ] || return 1
  echo "$(( $(now_ms) - t )) $c"
}
# The card's idle state from the newest sampler line, as JSON fields: minion clock (mhz.minion) and on-die minion
# voltage (die_mv.minion); null when absent (dry run, a line without the field). aifoundry1-c0 (firmware 1.4.1) rests in
# "low_power" at 300 MHz / 398 mV and stayed idle at 600 MHz after a launch (25 Sep clock test); the other cards idle at
# 600 MHz. With the per-sample clock in the telemetry, the reducer tells the idle state from these.
idle_state() {
  local l m v
  l=$(newest_line)
  m=$(sed -n 's/.*"mhz":{"minion":\([0-9]*\).*/\1/p' <<< "$l"); v=$(sed -n 's/.*"die_mv":{[^}]*"minion":\([0-9]*\).*/\1/p' <<< "$l")
  echo "\"idle_mhz\":${m:-null},\"idle_minion_mv\":${v:-null}"
}
sampler_alive() { dry && return 0; [ -n "${SAMPLER_PID:-}" ] && kill -0 "$SAMPLER_PID" 2>/dev/null; }
abort() {  # abort <exit code> <note>; exit code 3 = someone else is on the card: do not open it again
  mark abort "\"why\":\"$2\""
  [ "$1" = 3 ] && NO_CARD=1
  stop_sampler
  [ -f "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
  [ -f "$OUT/heater.out" ] && gzip -f "$OUT/heater.out"
  block_end fail "$2"
  exit "$1"
}

# ---- 1. the card must be free
others_present && exit 3
# a device process of this user on this card (another session, a leftover): the heater would land on its measurement
ours_running && { log "a device process of this user is running on this card: not starting"; exit 3; }
[ -x "$HEATER" ] && [ -x "$ETTELEM" ] || { log "missing $HEATER or $ETTELEM"; exit 1; }
N0=$(modcount)
if [ -n "$N0" ] && [ "$N0" != 0 ]; then log "et_soc1 use count $N0: someone holds the card; not starting"; exit 3; fi
[ "$MODCHECK" = on ] || log "et_soc1 use count not checked: V3_DEVICE=$V3_DEVICE, the module serves both cards"

# ---- 2. begin, sampler
block_begin "$EXPNAME" "$PASS_ARG"
[ -n "$SMOKE" ] && sha256sum "$HERE"/* >> "$OUT/code.sha256" 2>/dev/null
printf '{"exp":"%s","pass":%s,"card":"%s","variant":"%s","gov_free":%s,"v3_device":"%s","target_c":%s,"heat_max_bursts":%s,"heat_max_s":%s,"cool_s":%s,"heater":"%s","heater_args":"%s","sampler_every_ms":100,"sampler_s":%s,"modcount_check":"%s","modcount_before":"%s","dry":%s}\n' \
  "$EXPNAME" "$PASS_ARG" "$CARD" "$VARIANT" "$([ -n "$GOV_FREE" ] && echo true || echo false)" "${V3_DEVICE:-}" \
  "$TARGET_C" "$HEAT_MAX_BURSTS" "$HEAT_MAX_S" "$COOL_S" "$HEATER" "${HEAT_ARGS[*]}" \
  "$SAMPLER_S" "$MODCHECK" "${N0:-}" "$(dry && echo true || echo false)" > "$OUT/cycle.json"
: > "$OUT/launches.jsonl"; : > "$OUT/heat.jsonl"; : > "$OUT/marks.jsonl"
start_sampler "$OUT/telemetry.jsonl" "$SAMPLER_S" || { block_end fail "sampler did not start"; exit 1; }
NS=0                    # the use count with only our sampler open (max of 5 reads): the intrusion baseline
for i in 1 2 3 4 5; do n=$(modcount); [ -n "$n" ] && [ "$n" -gt "$NS" ] && NS=$n; dry || sleep 0.2; done
[ "$MODCHECK" = on ] || NS=
mark cycle_start "\"modcount_sampler\":\"${NS:-}\",$(idle_state)"
if [ -n "$NS" ]; then mc="sampler holds et_soc1 x$NS"; else mc="et_soc1 use count not checked"; fi
log "cycle $VARIANT: target ${TARGET_C} C, cool ${COOL_S} s, $mc, idle state $(idle_state)"

# ---- 3. heat
HEAT_T0=$(now_ms); nb=0; fails=0; reason=bursts; die=
while [ "$nb" -lt "$HEAT_MAX_BURSTS" ]; do
  if dry; then age=0   # a synthetic die: a governor-free card reaches 88 C, the pinned one plateaus at 63 C (the burst cap)
    if [ -n "$GOV_FREE" ]; then die=$(( 70 + 3 * nb )); else die=$(( 52 + nb / 4 )); [ "$die" -gt 63 ] && die=63; fi
  else
    r=; for i in 1 2 3 4 5 6 7 8 9 10; do r=$(live_reading) && [ "${r%% *}" -lt 3000 ] && break; r=; sleep 0.5; done
    [ -n "$r" ] || abort 1 "sampler output stale during heating"
    age=${r%% *}; die=${r##* }
  fi
  echo "{\"t_ms\":$(now_ms),\"die_c\":$die,\"age_ms\":$age,\"bursts\":$nb}" >> "$OUT/heat.jsonl"
  if [ -z "$SMOKE" ] && [ "$die" -ge "$TARGET_C" ]; then reason=target; break; fi
  if [ $(( $(now_ms) - HEAT_T0 )) -ge $(( HEAT_MAX_S * 1000 )) ]; then reason=time; break; fi
  others_present && abort 3 "another user arrived during heating"
  fp=$(foreign_procs)     # a device process on this card but our sampler (our heater is not running here)
  [ -n "${fp// /}" ] && abort 3 "device process appeared during heating: $fp"
  ts=$(now_ms)
  if dry; then hold10 "$HEATER" "${HEAT_ARGS[@]}"; rc=$?; else
    hold10 "$HEATER" "${HEAT_ARGS[@]}" >> "$OUT/heater.out" 2>&1; rc=$?; fi
  te=$(now_ms); nb=$(( nb + 1 ))
  echo "{\"t_start_ms\":$ts,\"t_end_ms\":$te,\"rc\":$rc,\"burst\":$nb}" >> "$OUT/launches.jsonl"
  if [ "$rc" -ne 0 ]; then fails=$(( fails + 1 )); [ "$fails" -ge 3 ] && abort 1 "heater failed 3 times in a row (rc $rc)"
  else fails=0; fi
done
if ! dry; then sleep 0.3; r=$(live_reading) && die=${r##* }; fi
mark heat_end "\"die_c\":${die:-null},\"reason\":\"$reason\",\"bursts\":$nb,\"heat_s\":$(( ($(now_ms) - HEAT_T0) / 1000 ))"
log "heated: $nb bursts, die ${die:-?} C ($reason)"

# ---- 4. cool: no launch for COOL_S seconds
mark cool_start
polls=0; oc_polls=0
if dry; then echo "DRY idle ${COOL_S} s: every 10 s check sampler alive, device processes on this card (V3_DEVICE=${V3_DEVICE:-none}), et_soc1 use count <= ${NS:-not checked}" >&2
else
  end=$(( $(now_ms) + COOL_S * 1000 )); logins_seen=
  while :; do
    left=$(( end - $(now_ms) )); [ "$left" -le 0 ] && break
    [ "$left" -gt 10000 ] && left=10000
    sleep "$(( left / 1000 )).$(printf '%03d' $(( left % 1000 )))"
    sampler_alive || abort 1 "sampler exited during the idle"
    sc=$(scan_procs); fp=$(awk '$1 == "F" {print $2}' <<< "$sc" | tr '\n' ' '); n=$(modcount)
    polls=$(( polls + 1 )); grep -q '^O ' <<< "$sc" && oc_polls=$(( oc_polls + 1 ))
    [ -n "${fp// /}" ] && abort 3 "device process appeared during the idle: $fp"
    [ -n "$n" ] && [ -n "$NS" ] && [ "$n" -gt "$NS" ] && abort 3 "et_soc1 use count $n > $NS during the idle"
    lg=$(other_logins)
    if [ -n "${lg// /}" ] && [ -z "$logins_seen" ]; then mark login "\"users\":\"$lg\""; logins_seen=1; fi
  done
fi
# other_card_polls: polls that saw our own device process on the other card of this host (the chassis shares its air)
mark cool_end "$(idle_state),\"polls\":$polls,\"other_card_polls\":$oc_polls"

# ---- 5. end
stop_sampler
dry || sleep 2          # block_end's die reading starts ettelem again; right after an instance it often fails
gzip -f "$OUT/telemetry.jsonl"; [ -f "$OUT/heater.out" ] && gzip -f "$OUT/heater.out"
note=$(python3 "$HERE/reduce.py" --check-pass "$OUT" 2> "$OUT/check.err"); rc=$?
[ -s "$OUT/check.err" ] || rm -f "$OUT/check.err"
if [ $rc -ne 0 ]; then block_end fail "check: ${note:-reduce.py failed}"; exit 1; fi
block_end ok "$note"
exit 0
