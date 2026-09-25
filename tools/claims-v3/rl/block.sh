#!/usr/bin/env bash
# V3-RL (PLAN3 section 2, "V3-RL"): ONE pass of the rings (half A), the memory levels (half B) and the relay on
# the local card, the way run_rings_levels_power.sh + run_onchip_power.sh measure them (ettelem at 10 Hz, 5 s
# bursts bracketed by 10 s of idle), with the plan's changes: every device process under hold10 (timeout 10) and
# --budget 8; spin brackets (nocbench spin first and last in half A, memhier spin first and last in half B);
# ABBA l2/scp-local (BAAB on even passes); the ring order reversed on even passes; a scratchpad contents prefill
# (enercat tstore, zeros on odd passes, random on even) before scp-local and before scp-remote; on aifoundry2 the
# die heated to >= 76 C before each half and before the relay (lib.sh heat_to; a no-op on aifoundry3).
#
#   bash tools/claims-v3/rl/block.sh <pass> [--smoke]        (V3_DRY=1 prints the device calls instead)
#
# Output: $DATA_ROOT/rl/p<pass>/{A,B,relay}/{telemetry.jsonl.gz,runs.jsonl,marks.jsonl,launches.jsonl,...},
# pass.json, heat-*.jsonl, quality.json, block.json. Reduce with tools/claims-v3/rl/reduce.py (README.md).
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
cd "$V3_ROOT" || exit 2
others_present && exit 3
# our own device process still running (another block or smoke started by hand, a sampler that did not exit):
# never two of ours on the card; exit 3 so the queue waits and retries
ours_running && { log "rl: one of our device processes is still running"; exit 3; }

K=${1:?usage: block.sh <pass> [--smoke]}
case "$K" in '' | *[!0-9]* | 0) echo "pass must be a positive integer" >&2; exit 2 ;; esac
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1

SECS=5          # seconds of launches per burst (run_rings_levels_power.sh default)
GAP=10          # idle seconds after every burst: analyze_reruns.reduce_dir takes its idle brackets from these
RELAY_SECS=8    # seconds per relay medium (run_reruns_warm.sh called run_onchip_power.sh <dir> 8)
LEAD=8; TAIL=6  # idle before the first burst and after the last one, as in the committed runners
if [ -n "$SMOKE" ]; then SECS=0.5; GAP=1; RELAY_SECS=0; LEAD=2; TAIL=1; fi
if [ $((K % 2)) = 1 ]; then CONTENTS=zeros; EVEN=; else CONTENTS=random; EVEN=1; fi
ERRLOG_DRY=; [ -n "${V3_DRY:-}" ] && ERRLOG_DRY=/dev/stderr   # dry run: show the DRY lines instead of logging them

pause() { [ -n "${V3_DRY:-}" ] || sleep "$1"; }
count() { local c; c=$(grep -c "$1" "$2" 2>/dev/null); echo "${c:-0}"; }   # matching lines, 0 if no file
# bail <note> [exit code]: the one failure path. The sampler is stopped (SIGTERM, lib.sh) before anything else, the
# telemetry written so far is gzipped, block.json records the failure, and the block exits (1, or 3 = retry later).
bail() {
  stop_sampler
  if [ -n "${OUT:-}" ]; then
    local f; for f in "$OUT"/*/telemetry.jsonl; do [ -f "$f" ] && gzip -f "$f"; done
    block_end fail "$1"
  fi
  exit "${2:-1}"
}
BAD=; NBAD=0
# launch <out-file> <dir> <label> <tag> <cmd...>: one device process under hold10; its "<tag> {json}" lines go to
# <out-file> with the label added, its exit status to launches.jsonl. A launch that hit the 10 s cap (timeout's
# 124, or 137) stops the pass at once, and so does a third failed launch (not in a smoke, which reports them all):
# the pass must be re-run anyway, and a card that fails launches is not held any longer.
launch() {
  local of=$1 d=$2 lab=$3 tag=$4; shift 4
  local t0 rc; t0=$(now_ms)
  # nocbench prints only throughput lines for shift and spin; keep the committed runner's filter anyway
  hold10 "$@" 2>> "${ERRLOG_DRY:-$d/stderr.log}" | grep "^$tag {" |
    { if [ "$tag" = NOCBENCH ]; then grep '"kind":"throughput"'; else cat; fi; } |
    sed "s/^$tag {/{\"label\":\"$lab\",/" >> "$of"
  rc=${PIPESTATUS[0]}
  printf '{"label":"%s","t0_ms":%s,"t1_ms":%s,"rc":%s,"cmd":"%s"}\n' "$lab" "$t0" "$(now_ms)" "$rc" "$*" >> "$d/launches.jsonl"
  [ "$rc" = 0 ] && return 0
  BAD="$BAD $lab:rc$rc"; NBAD=$((NBAD + 1))
  case "$rc" in 124 | 137) bail "launch $lab hit the 10 s cap (rc $rc):$BAD" ;; esac
  [ -z "$SMOKE" ] && [ "$NBAD" -ge 3 ] && bail "3 launches failed:$BAD"
  return 1
}
mark() { printf '{"label":"%s","t_ms":%s}\n' "$2" "$(now_ms)" >> "$1/marks.jsonl"; }
# burst <dir> <label> <tag> <cmd...>: a mark, one launch of SECS seconds, then GAP seconds of idle.
burst() { local d=$1 lab=$2 tag=$3; shift 3; mark "$d" "$lab"; launch "$d/runs.jsonl" "$d" "$lab" "$tag" "$@"; pause "$GAP"; }

ring_args() {  # label -> nocbench --rings/--count (run_rings_levels_power.sh)
  case "$1" in
    pair) echo "pair 32" ;; neigh) echo "neigh 32" ;; shire) echo "shire 32" ;;
    xshire1) echo "xshire:1 32" ;; xshire16) echo "xshire:16 32" ;; xshire8) echo "xshire:8 32" ;;
    xshire2) echo "xshire:2 32" ;; xshire4) echo "xshire:4 32" ;; xshire6) echo "xshire:6 32" ;;
    shire-c4) echo "shire 4" ;; xshire1-c4) echo "xshire:1 4" ;;
    *) echo "unknown ring $1" >&2; return 1 ;;
  esac
}
level_args() {  # label (optional -1/-2 ABBA or -first/-last suffix) -> memhier arguments (run_rings_levels_power.sh)
  local b=${1%-[12]}; b=${b%-first}; b=${b%-last}
  case "$b" in
    mspin) echo "--test spin" ;;
    l1) echo "--test l1" ;;
    l2) echo "--test stream --where dram --bytes-per-minion 8K" ;;
    l3) echo "--test stream --where dram --bytes-per-minion 24K" ;;
    dram) echo "--test stream --where dram --bytes-per-minion 256K" ;;
    scp-local) echo "--test stream --where scp-local --bytes-per-minion 64K" ;;
    scp-remote) echo "--test stream --where scp-remote --bytes-per-minion 64K --scp-shift 16" ;;
    *) echo "unknown level $1" >&2; return 1 ;;
  esac
}
ring() { local a; a=($(ring_args "$2")); burst "$1" "$2" NOCBENCH "$NOCBENCH" --test shift --rings "${a[0]}" --count "${a[1]}" --seconds "$SECS" --budget 8; }
nspin() { burst "$1" "$2" NOCBENCH "$NOCBENCH" --test spin --seconds "$SECS" --budget 8; }
level() { local a; a=($(level_args "$2")); burst "$1" "$2" MEMHIER "$MEMHIER" "${a[@]}" --seconds "$SECS" --budget 8; }
# The contents prefill (PLAN3 V3-RL build/sync): enercat tensor stores of zeros or random fp32 into every compute
# shire's own scratchpad, 64 KB per minion. enercat writes its slices from scratchpad offset 256 KB
# (enercat host main.cpp: a.scp_off = 256 * 1024), memhier reads its scp-local/scp-remote buffers from offset 0
# (memhier host: stream_base 0 for the scratchpad), so the prefill covers the buffers of memhier minions 4-31
# (28 of 32, 87.5% of the bytes read); offset 0-256 KB cannot be written (a tensor store there faults,
# docs/findings/18-on-chip-relay.md). README.md records this deviation.
prefill() {
  local d=$1 why=$2
  mark "$d" "prefill:$why"
  launch "$d/prefill.jsonl" "$d" "prefill:$why" ENERCAT "$ENERCAT" --pattern tstore --operands "$CONTENTS" \
    --slice-bytes 64K --scp --seconds "$([ -n "$SMOKE" ] && echo 0.1 || echo 0.3)" --window 60000000 --budget 8
  pause "$GAP"   # the burst that follows takes its before-idle from 6 s before it: keep the prefill out of it
}
relay_medium() {  # dir medium stages [label]: back-to-back ~0.9 s relay launches for RELAY_SECS (one in a smoke)
  local d=$1 med=$2 k=$3 lab=${4:-$2} end
  printf '{"label":"%s","stages":%s,"t_ms":%s}\n' "$lab" "$k" "$(now_ms)" >> "$d/marks.jsonl"
  end=$(( $(date +%s) + RELAY_SECS ))
  while :; do
    launch "$d/runs.jsonl" "$d" "$lab" ONCHIP "$ONCHIP" --test relay --medium "$med" --stage-bytes 1M --stages "$k" --work 1 --budget 8 ||
      break   # a failed launch is not retried for the rest of the medium's seconds
    [ -n "${V3_DRY:-}" ] && break
    [ "$(date +%s)" -lt "$end" ] || break
  done
  pause "$GAP"
}
start_half() {  # dir seconds: the half's own sampler (lib.sh start_sampler: first-line wait, retries, one drain)
  mkdir -p "$1"
  start_sampler "$1/telemetry.jsonl" "$2" || bail "sampler failed to start ($(basename "$1"))"
  pause "$LEAD"
}
end_half() { pause "$TAIL"; stop_sampler; }
heat() {  # aifoundry2: die >= 76 C before each half and the relay (sampler stopped: heat_to opens the management node)
  stop_sampler   # none runs here; kept so a later edit cannot put heat_to next to a running sampler
  heat_to 76 "$OUT/heat-$1.jsonl" || bail "heat_to 76 gave up before $1"
}
between() {  # another user arrived mid-pass: stop politely, the queue retries the pass later (exit 3)
  others_present && bail "others present before $1: pass abandoned" 3
  ours_running && bail "one of our device processes still running before $1: pass abandoned" 3
}
trap 'bail "terminated by signal" 143' TERM INT

# ---- the order inside the pass (written to pass.json before anything runs) ----
RINGS=(pair neigh shire xshire1 xshire16 xshire8 xshire2 xshire4 xshire6 shire-c4 xshire1-c4)
if [ -n "$EVEN" ]; then r=(); for ((i = ${#RINGS[@]} - 1; i >= 0; i--)); do r+=("${RINGS[i]}"); done; RINGS=("${r[@]}"); fi
if [ -z "$EVEN" ]; then ABBA=(l2-1 prefill scp-local-1 scp-local-2 l2-2)       # odd: A B B A
else ABBA=(prefill scp-local-1 l2-1 l2-2 scp-local-2); fi                    # even: B A A B
LEVELS=(mspin-first "${ABBA[@]}" l1 l3 dram prefill scp-remote mspin-last)
MEDIA=(dram:640 scp:19000 hop:7800)   # run_onchip_power.sh stages_for: about 1 s of device time per launch

if [ -n "$SMOKE" ]; then
  # ---- smoke: every component once, shortest real launches (about 20 s of device time) ----
  block_begin rl-smoke "$K"
  sha256sum tools/claims-v3/rl/* >> "$OUT/code.sha256" 2>/dev/null || true
  S=$OUT/S; mkdir -p "$S"
  start_half "$S" 120
  nspin "$S" nspin-first
  ring "$S" pair
  ring "$S" xshire1-c4
  level "$S" mspin-first
  for lab in l1 l2-1 l3 dram; do level "$S" "$lab"; done
  prefill "$S" scp-local
  level "$S" scp-local-1
  level "$S" scp-remote
  for m in "${MEDIA[@]}"; do relay_medium "$S" "${m%%:*}" "${m##*:}" "relay-${m%%:*}"; done
  end_half
  if [ "$CARD" = aifoundry2 ]; then   # the heater binary once (1 s), after the sampler has stopped
    launch "$S/heater.jsonl" "$S" heater SPARSITY "$HEATER" --test fma --type fp32 --pattern none --values randn \
      --shires 0xffffffff --per-shire 32 --seconds 1 --seed 1
    echo "{\"die_c\":\"$(die_c)\"}" >> "$S/heater.jsonl"
  fi
  if [ -n "${V3_DRY:-}" ]; then block_end ok "dry run"; exit 0; fi
  miss=
  for lab in nspin-first pair xshire1-c4 mspin-first l1 l2-1 l3 dram scp-local-1 scp-remote relay-dram relay-scp relay-hop; do
    grep -q "\"label\":\"$lab\".*\"ok\":true" "$S/runs.jsonl" 2>/dev/null || miss="$miss $lab"
  done
  grep -q '"label":"prefill:scp-local".*"ok":true' "$S/prefill.jsonl" 2>/dev/null || miss="$miss prefill"
  nt=$(count '^{' "$S/telemetry.jsonl")
  [ "$nt" -gt 50 ] || miss="$miss telemetry($nt)"
  gzip -f "$S/telemetry.jsonl"
  if [ -z "$miss$BAD" ]; then block_end ok "smoke: all components ran ($nt samples)"; exit 0; fi
  block_end fail "smoke: missing$miss rc$BAD"; exit 1
fi

block_begin rl "$K"
printf '{"pass":%s,"card":"%s","contents":"%s","rings":"%s","levels":"%s","media":"%s","secs":%s,"gap_s":%s,"relay_secs":%s,"dry":%s}\n' \
  "$K" "$CARD" "$CONTENTS" "${RINGS[*]}" "${LEVELS[*]}" "${MEDIA[*]}" "$SECS" "$GAP" "$RELAY_SECS" \
  "$([ -n "${V3_DRY:-}" ] && echo true || echo false)" > "$OUT/pass.json"

# ---- half A: nocbench spin, the eleven rings (reversed on even passes), nocbench spin ----
heat A
A=$OUT/A; start_half "$A" 420
nspin "$A" nspin-first
for r in "${RINGS[@]}"; do ring "$A" "$r"; done
nspin "$A" nspin-last
end_half
between "half B"

# ---- half B: memhier spin, ABBA l2/scp-local with the prefill, l1, l3, dram, prefill, scp-remote, memhier spin ----
heat B
B=$OUT/B; start_half "$B" 420
nxt=scp-local
for lab in "${LEVELS[@]}"; do
  if [ "$lab" = prefill ]; then prefill "$B" "$nxt"; nxt=scp-remote; else level "$B" "$lab"; fi
done
end_half
between "the relay"

# ---- the relay: DRAM, own scratchpad, next shire's scratchpad (run_onchip_power.sh, timeout 40 -> hold10) ----
heat relay
R=$OUT/relay; start_half "$R" 200
for m in "${MEDIA[@]}"; do relay_medium "$R" "${m%%:*}" "${m##*:}"; done
end_half

# ---- quality: the drop rules the reducer applies, checked now so a pass that must be re-run is marked failed ----
if [ -n "${V3_DRY:-}" ]; then block_end ok "dry run"; exit 0; fi
miss=; off=0; tot=0; short=
for lab in nspin-first "${RINGS[@]}" nspin-last; do grep -q "\"label\":\"$lab\"" "$A/runs.jsonl" 2>/dev/null || miss="$miss A:$lab"; done
for lab in "${LEVELS[@]}"; do [ "$lab" = prefill ] && continue; grep -q "\"label\":\"$lab\"" "$B/runs.jsonl" 2>/dev/null || miss="$miss B:$lab"; done
for w in scp-local scp-remote; do grep -q "\"label\":\"prefill:$w\".*\"ok\":true" "$B/prefill.jsonl" 2>/dev/null || miss="$miss B:prefill:$w"; done
for m in "${MEDIA[@]}"; do grep -q "\"label\":\"${m%%:*}\"" "$R/runs.jsonl" 2>/dev/null || miss="$miss relay:${m%%:*}"; done
for h in A B relay; do
  f=$OUT/$h/telemetry.jsonl
  n=$(count '^{' "$f"); ok=$(count '"mhz":{"minion":600,' "$f")
  tot=$((tot + n)); off=$((off + n - ok))
  [ "$n" -gt 300 ] || short="$short $h($n)"
  gzip -f "$f"
done
printf '{"samples":%s,"off600":%s,"missing":"%s","short":"%s","rc":"%s"}\n' "$tot" "$off" "${miss# }" "${short# }" "${BAD# }" > "$OUT/quality.json"
# PLAN3 common rules: an aifoundry2 repeat with any sample off 600 MHz is dropped and re-run (schedule the pass
# again: queue.sh skips ok passes). aifoundry3 is pinned at 600 MHz; there only V3-RL's burst rule applies (clock
# off 600 MHz in > 2% of a burst's samples drops that burst, in reduce.py), so its off-600 count is recorded only.
offbad=0; [ "$CARD" = aifoundry2 ] && [ "$off" -gt 0 ] && offbad=1
if [ "$offbad" = 1 ] || [ -n "$miss$short$BAD" ]; then
  block_end fail "off600=$off of $tot; missing:${miss:- none}; short:${short:- none}; rc:${BAD:- none}"; exit 1
fi
block_end ok "contents $CONTENTS; $tot samples, $off off 600 MHz"
