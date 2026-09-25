#!/usr/bin/env bash
# V3-IDLE (PLAN3 §2 "V3-IDLE", suggested E44): ONE heat/cool cycle on the local card.
#
#   bash tools/claims-v3/idle/block.sh <pass> [--smoke]
#
#   pass 1-9    a short cycle: heat, then 900 s with no launch            (items IDLE-0, a-f, k)
#   pass 11-19  an IDLE-LONG cycle: heat, then 5400 s (aifoundry2) or     (item IDLE-L; also a cycle for 0, a-f, k,
#               2700 s (aifoundry3) with no launch; overnight only,        using its first 900 s of cooling)
#               from a schedule of its own (one block of ~95 / ~60 min)
#   --smoke     the smallest real check of every component (~30 s of card time): sampler, live die reading from
#               the sampler, two heater bursts, 20 s idle with the intrusion poll, pass check by reduce.py
#
# One pass, in order:
#   1. nobody else on the card (lib others_present; et_soc1 use count 0), else exit 3 (the queue retries)
#   2. block_begin (die reading, card closed again), then the 10 Hz sampler for the whole cycle
#   3. heat: 2 s random-data fma bursts on all 1024 minions (lib HEATER: sparsity_t2 on aifoundry2, sparsity on
#      aifoundry3; each under hold10) until the die reads >= target (aifoundry2 88 C; aifoundry3 90 C, i.e. its
#      plateau), at most 150 bursts or 900 s. The die is read from the running sampler's own output, never with a
#      second opener of the management node.
#   4. cool: no launch for COOL_S seconds; every 10 s check that the sampler is alive and that nobody opened the
#      card (a device process other than our sampler, or the et_soc1 use count above the sampler's own); an
#      intrusion stops the cycle (block_end fail, exit 3), because another kernel spoils the idle samples.
#   5. SIGTERM the sampler, gzip the telemetry, check the pass (reduce.py --check-pass), block_end.
# Files in $OUT: telemetry.jsonl.gz (10 Hz), launches.jsonl (every burst: t_start_ms, t_end_ms, rc), heat.jsonl
# (the die reading before every burst), marks.jsonl (cycle_start, heat_end, cool_start, cool_end, abort),
# cycle.json (the cycle's parameters), heater.out.gz (the heater's stdout), check.json, block.json.
set -u
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"     # cd's to the tree root; CARD, HEATER, ETTELEM, DATA_ROOT, helpers

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

if [ -n "$SMOKE" ]; then
  EXPNAME=idle-smoke; VARIANT=smoke; COOL_S=20; HEAT_MAX_BURSTS=2; HEAT_MAX_S=30
else
  EXPNAME=idle; HEAT_MAX_BURSTS=150; HEAT_MAX_S=900
  if [ "$PASS_ARG" -ge 1 ] && [ "$PASS_ARG" -le 9 ]; then VARIANT=short; COOL_S=900
  elif [ "$PASS_ARG" -ge 11 ] && [ "$PASS_ARG" -le 19 ]; then
    VARIANT=long; if [ "$CARD" = aifoundry2 ]; then COOL_S=5400; else COOL_S=2700; fi
  else echo "pass must be 1-9 (short cycle) or 11-19 (IDLE-LONG)" >&2; exit 2
  fi
fi
if [ "$CARD" = aifoundry2 ]; then TARGET_C=88; else TARGET_C=90; fi   # aifoundry3: never reached, heat to plateau
SAMPLER_S=$(( HEAT_MAX_S + COOL_S + 90 ))                              # outlives the cycle; stopped with SIGTERM
HEAT_ARGS=(--test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1)

dry() { [ -n "${V3_DRY:-}" ]; }
# et_soc1 module use count (who holds the card open). Reads /proc/modules only.
modcount() { if dry; then echo 0; else lsmod 2>/dev/null | awk '$1=="et_soc1"{print $3}'; fi; }
# Device processes other than our own sampler (any user), by executable name as lib.sh recognises them.
foreign_procs() {
  dry && return 0
  ps -eo uid=,pid=,comm= | awk -v sp="${SAMPLER_PID:-0}" -v re="$DEV_COMM" '$3 ~ re && $2 != sp {print $1":"$2":"$3}' | tr '\n' ' '
}
other_logins() { who | awk '{print $1}' | sort -u | grep -vx "$USER" | tr '\n' ' ' || true; }
mark() {  # mark <event> [extra JSON fields, already formatted: "\"k\":v,..."]
  local extra=${2:-}; [ -n "$extra" ] && extra=",$extra"
  echo "{\"t_ms\":$(now_ms),\"ev\":\"$1\"$extra}" >> "$OUT/marks.jsonl"
}
# The newest complete sampler line: "<age_ms> <die_c>"; non-zero if there is none.
live_reading() {
  local l t c
  l=$(tail -n 4 "$SAMPLER_OUT.raw" 2>/dev/null | grep '^{.*}$' | tail -n 1)
  [ -n "$l" ] || return 1
  t=$(sed -n 's/^{"t_ms":\([0-9]*\),.*/\1/p' <<< "$l"); c=$(sed -n 's/.*"minshire":\[\([0-9]*\).*/\1/p' <<< "$l")
  [ -n "$t" ] && [ -n "$c" ] || return 1
  echo "$(( $(now_ms) - t )) $c"
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
# a device process of this user (another session, a leftover): the heater would land on its measurement
ours_running && { log "a device process of this user is running: not starting"; exit 3; }
[ -x "$HEATER" ] && [ -x "$ETTELEM" ] || { log "missing $HEATER or $ETTELEM"; exit 1; }
N0=$(modcount)
if [ -n "$N0" ] && [ "$N0" != 0 ]; then log "et_soc1 use count $N0: someone holds the card; not starting"; exit 3; fi

# ---- 2. begin, sampler
block_begin "$EXPNAME" "$PASS_ARG"
[ -n "$SMOKE" ] && sha256sum "$HERE"/* >> "$OUT/code.sha256" 2>/dev/null
printf '{"exp":"%s","pass":%s,"card":"%s","variant":"%s","target_c":%s,"heat_max_bursts":%s,"heat_max_s":%s,"cool_s":%s,"heater":"%s","heater_args":"%s","sampler_every_ms":100,"sampler_s":%s,"modcount_before":"%s","dry":%s}\n' \
  "$EXPNAME" "$PASS_ARG" "$CARD" "$VARIANT" "$TARGET_C" "$HEAT_MAX_BURSTS" "$HEAT_MAX_S" "$COOL_S" "$HEATER" "${HEAT_ARGS[*]}" \
  "$SAMPLER_S" "${N0:-}" "$(dry && echo true || echo false)" > "$OUT/cycle.json"
: > "$OUT/launches.jsonl"; : > "$OUT/heat.jsonl"; : > "$OUT/marks.jsonl"
start_sampler "$OUT/telemetry.jsonl" "$SAMPLER_S" || { block_end fail "sampler did not start"; exit 1; }
NS=0                    # the use count with only our sampler open (max of 5 reads): the intrusion baseline
for i in 1 2 3 4 5; do n=$(modcount); [ -n "$n" ] && [ "$n" -gt "$NS" ] && NS=$n; dry || sleep 0.2; done
mark cycle_start "\"modcount_sampler\":\"${NS:-}\""
log "cycle $VARIANT: target ${TARGET_C} C, cool ${COOL_S} s, sampler holds et_soc1 x${NS:-?}"

# ---- 3. heat
HEAT_T0=$(now_ms); nb=0; fails=0; reason=bursts; die=
while [ "$nb" -lt "$HEAT_MAX_BURSTS" ]; do
  if dry; then age=0   # a synthetic die: aifoundry2 reaches 88 C, aifoundry3 plateaus at 63 C (the burst cap ends it)
    if [ "$CARD" = aifoundry2 ]; then die=$(( 70 + 3 * nb )); else die=$(( 52 + nb / 4 )); [ "$die" -gt 63 ] && die=63; fi
  else
    r=; for i in 1 2 3 4 5 6 7 8 9 10; do r=$(live_reading) && [ "${r%% *}" -lt 3000 ] && break; r=; sleep 0.5; done
    [ -n "$r" ] || abort 1 "sampler output stale during heating"
    age=${r%% *}; die=${r##* }
  fi
  echo "{\"t_ms\":$(now_ms),\"die_c\":$die,\"age_ms\":$age,\"bursts\":$nb}" >> "$OUT/heat.jsonl"
  if [ -z "$SMOKE" ] && [ "$die" -ge "$TARGET_C" ]; then reason=target; break; fi
  if [ $(( $(now_ms) - HEAT_T0 )) -ge $(( HEAT_MAX_S * 1000 )) ]; then reason=time; break; fi
  others_present && abort 3 "another user arrived during heating"
  fp=$(foreign_procs)     # any user's device process but our sampler (our heater is not running here)
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
if dry; then echo "DRY idle ${COOL_S} s: every 10 s check sampler alive, foreign device processes, et_soc1 use count <= ${NS:-?}" >&2
else
  end=$(( $(now_ms) + COOL_S * 1000 )); logins_seen=
  while :; do
    left=$(( end - $(now_ms) )); [ "$left" -le 0 ] && break
    [ "$left" -gt 10000 ] && left=10000
    sleep "$(( left / 1000 )).$(printf '%03d' $(( left % 1000 )))"
    sampler_alive || abort 1 "sampler exited during the idle"
    fp=$(foreign_procs); n=$(modcount)
    [ -n "${fp// /}" ] && abort 3 "device process appeared during the idle: $fp"
    [ -n "$n" ] && [ -n "$NS" ] && [ "$n" -gt "$NS" ] && abort 3 "et_soc1 use count $n > $NS during the idle"
    lg=$(other_logins)
    if [ -n "${lg// /}" ] && [ -z "$logins_seen" ]; then mark login "\"users\":\"$lg\""; logins_seen=1; fi
  done
fi
mark cool_end

# ---- 5. end
stop_sampler
dry || sleep 2          # block_end's die reading starts ettelem again; right after an instance it often fails
gzip -f "$OUT/telemetry.jsonl"; [ -f "$OUT/heater.out" ] && gzip -f "$OUT/heater.out"
note=$(python3 "$HERE/reduce.py" --check-pass "$OUT" 2> "$OUT/check.err"); rc=$?
[ -s "$OUT/check.err" ] || rm -f "$OUT/check.err"
if [ $rc -ne 0 ]; then block_end fail "check: ${note:-reduce.py failed}"; exit 1; fi
block_end ok "$note"
exit 0
