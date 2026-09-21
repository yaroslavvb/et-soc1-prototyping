#!/usr/bin/env bash
# Long runs of the matmul value patterns: minutes instead of seconds, to see the slow thermal stages and to
# tie temperature to switching activity (docs/reports: horace-experiment, section on long runs).
#
# Each line of the schedule file is one run:   <values> <minions-per-shire> <max-seconds> <seed>
# Every run starts like the strict experiment: random-data bursts heat the die to <preheat_c> if it is below
# that, the card idles until the mean minion-shire sensor first reads <target_c> (or <max_wait_s> pass), and
# the pattern then runs as ONE process for up to <max-seconds>. The run ends early, between two 0.5 s
# launches, when the reading reaches <cap_c> (the host's --stop-file), when board power reaches 73 W (the
# PMIC's alarm is at 75 W), or when telemetry goes stale.
# No new run starts after <deadline_s> of session time; a final idle stretch records the cool-down.
# The 10 s etiquette limit is waived for this experiment by the user; between runs the script still waits
# while anyone else has the card open.
#
#   tools/ettelem/run_horace_long.sh <out-dir> <schedule> [target_c=80] [preheat_c=84] [cap_c=90] \
#       [max_wait_s=900] [deadline_s=18600] [final_idle_s=900]
set -u
out=${1:?out dir}; sched=${2:?schedule file}; target=${3:-80}; preheat=${4:-84}; cap=${5:-90}
maxwait=${6:-900}; deadline=${7:-18600}; final_idle=${8:-900}
mkdir -p "$out/tiles"; sched=$(readlink -f "$sched"); cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
build/ettelem/ettelem sample --seconds 25000 --every-ms 100 2>/dev/null | grep --line-buffered '^{' > "$out/telemetry.jsonl" &
S=$!
trap 'kill $S 2>/dev/null; rm -f "$out/stop"' EXIT
: > "$out/runs.jsonl"; : > "$out/starts.jsonl"; : > "$out/ends.jsonl"
t_session=$(date +%s)
line() { tail -n 2 "$out/telemetry.jsonl" | head -n 1; }
temp() { line | sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p'; }
watts() { line | sed -n 's/.*"board_w":\([0-9]*\)\..*/\1/p'; }
age_ms() { local t; t=$(line | sed -n 's/^{"t_ms":\([0-9]*\),.*/\1/p'); [ -n "$t" ] && echo $(( $(date +%s%3N) - t )) || echo 999999; }
burst() {  # a 2 s random-data burst, as in the strict experiment
  timeout 10 build/sparsity/host/sparsity_host --test fma --type fp32 --pattern none --values randn --shires 0xffffffff \
    --per-shire 32 --seconds 2 --seed 1 2>/dev/null < /dev/null | grep SPARSITY | sed "s/^SPARSITY //; s/^{/{\"block\":-9,/" >> "$out/runs.jsonl"
}
others() {  # open handles on the card besides our sampler
  local n; n=$(lsmod | awk '$1=="et_soc1"{print $3}'); echo $(( ${n:-1} - 1 ))
}
approach() {
  local t0; t0=$(date +%s)
  for i in $(seq 1 60); do
    t=$(temp); [ -n "$t" ] && [ "$t" -ge "$preheat" ] && break
    burst
  done
  while :; do
    t=$(temp); [ -n "$t" ] && [ "$t" -le "$target" ] && return 0
    [ $(( $(date +%s) - t0 )) -ge "$maxwait" ] && return 1
    sleep 0.2
  done
}
sleep 3
n=0
while read -r values pershire maxs seed <&3; do
  case "$values" in ''|\#*) continue;; esac
  [ $(( $(date +%s) - t_session )) -ge "$deadline" ] && { echo "deadline reached before run $n" >&2; break; }
  for i in $(seq 1 120); do [ "$(others)" -le 0 ] && break; sleep 5; done   # someone else has the card: wait up to 10 min
  t_a=$(date +%s%3N)
  approach; reached=$?
  dump="$out/tiles/$values.$seed.bin"; [ -e "$dump" ] && dump=""
  case "$values" in file:*) dump="";; esac   # custom tiles are already a file
  rm -f "$out/stop"
  echo "{\"run\":$n,\"values\":\"$values\",\"per_shire\":$pershire,\"max_s\":$maxs,\"seed\":$seed,\"start_temp\":$(temp),\"reached_target\":$(( 1 - reached )),\"approach_ms\":$(( $(date +%s%3N) - t_a )),\"t_ms\":$(date +%s%3N)}" >> "$out/starts.jsonl"
  timeout $(( maxs + 40 )) build/sparsity/host/sparsity_host < /dev/null --test fma --type fp32 --pattern none --values "$values" \
    --shires 0xffffffff --per-shire "$pershire" --seconds "$maxs" --budget $(( maxs + 30 )) --seed "$seed" --stop-file "$out/stop" ${dump:+--dump-tiles "$dump"} 2>/dev/null |
    grep --line-buffered SPARSITY | sed -u "s/^SPARSITY //; s/^{/{\"block\":$n,/" >> "$out/runs.jsonl" &
  H=$!
  reason=time
  while kill -0 $H 2>/dev/null; do
    t=$(temp)
    if [ -n "$t" ] && [ "$t" -ge "$cap" ]; then reason=cap; touch "$out/stop"; break; fi
    w=$(watts); if [ -n "$w" ] && [ "$w" -ge 73 ]; then reason=power; touch "$out/stop"; break; fi
    if [ "$(age_ms)" -gt 5000 ]; then reason=stale; touch "$out/stop"; break; fi
    sleep 0.5
  done
  wait $H 2>/dev/null
  echo "{\"run\":$n,\"values\":\"$values\",\"reason\":\"$reason\",\"end_temp\":$(temp),\"t_ms\":$(date +%s%3N)}" >> "$out/ends.jsonl"
  rm -f "$out/stop"
  [ "$reason" = stale ] && { echo "telemetry went stale; stopping the session" >&2; break; }
  n=$(( n + 1 ))
done 3< "$sched"
sleep "$final_idle"
echo done
