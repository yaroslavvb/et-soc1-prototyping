#!/usr/bin/env bash
# V3-TEL, one pass on the local card (PLAN3 §2 "V3-TEL": E-hub-1, pt-spatial X4/X2/X3, dvfs EXP-dvfs-2).
#
#   bash tools/claims-v3/tel/block.sh <pass> [--smoke]        (V3_DRY=1 prints every device call instead)
#
# One pass = four phases, in this order (README.md has the timings, the drops and every deviation from the plan):
#   1 governor readouts at INFO, no sampler: sptrace sp0, etcfg, 5 x 2 s fma-zeros launches 3 s apart, sptrace sp1,
#     ettelem config, firmware revisions (aifoundry2: heater first if the die is below 68 C);
#   2 the arms: [a2 heat to 76 C] SPST enable + extract, 60 s quiet, then Q PWR L10 E10 E20 E40 VOLT in an order drawn
#     per pass (tel_util.py order <card*100+pass>), each followed by an SPST extract and 30 s quiet; before each arm a
#     wrap guard waits in quiet if the SP stats ring could wrap inside the arm;
#   3 [a2 reheat] reset segment: ettelem --reset-ms 1000 while three 3 s enercat fmadd_ps bursts run 10 s apart, then
#     SPST enable (ettelem's reset turns the SP stats trace off, see README) and an extract;
#   4 [a2 reheat] DEBUG block: loglevel debug, idle sptrace, the X2 load/after captures around a 7 s randn burst, three
#     14 s --reset-ms windows with a 7 s randn burst 3 s in and an sptrace after each, one idle window; loglevel info.
# Every device process runs under hold10 (timeout 10); samplers only through start_sampler/stop_sampler (SIGTERM);
# nothing else opens the management node while a sampler runs. The EXIT trap stops the sampler, re-enables the SP
# stats trace and restores the INFO log level.
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"          # cd's to the tree root, sets CARD, binaries, DATA_ROOT
PASS=${1:?usage: block.sh <pass> [--smoke]}
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
others_present && exit 3

TEL=tools/claims-v3/tel
DRY=${V3_DRY:-}
EXPN=tel; [ -n "$SMOKE" ] && EXPN=tel-smoke
# A leftover directory of this pass (interrupted, or V3_FORCE=1 over a finished one) is set aside, never appended to
PDIR=$DATA_ROOT/$EXPN/p$PASS
if [ -d "$PDIR" ] && { [ ! -e "$PDIR/block.json" ] || [ -n "${V3_FORCE:-}" ]; }; then
  if [ -n "$SMOKE" ]; then rm -rf "$PDIR"; else mv "$PDIR" "$PDIR.attempt-$(date +%s)"; fi
fi
block_begin "$EXPN" "$PASS"
[ -n "$SMOKE" ] && sha256sum tools/claims-v3/lib.sh $TEL/* > "$OUT/code.sha256" 2>/dev/null
mkdir -p "$OUT/gov" "$OUT/trace" "$OUT/dbg"
CARDN=${CARD#aifoundry}

# ---- durations (s) and counts: the full pass, or the smoke check (<= 60 s of card time)
if [ -z "$SMOKE" ]; then
  Q0=60 GAP=30 QARM=60 PWR_S=60 L10_N=450 E10_S=60 E20_S=60 E40_S=30 VOLT_S=60
  GOV_N=5 GOV_S=2 R_PRE=5 R_GAP=10 R_POST=12 R_N=3 R_BURST=3
  X2_S=7 X2_AT=4 X2_AFTER=20 W_N=3 W_S=14 W_AT=3 W_BURST=7 W_GAP=30 W_IDLE=1
else
  Q0=1 GAP=0 QARM=1 PWR_S=2 L10_N=8 E10_S=2 E20_S=2 E40_S=2 VOLT_S=1
  GOV_N=1 GOV_S=1 R_PRE=2 R_GAP=0 R_POST=3 R_N=1 R_BURST=1
  X2_S=0 X2_AT=0 X2_AFTER=0 W_N=1 W_S=6 W_AT=2 W_BURST=1 W_GAP=0 W_IDLE=0
fi

# ---- helpers
zz() { if [ -n "$DRY" ]; then echo "DRY sleep $1" >&2; else sleep "$1"; fi; }
mark() { echo "{\"t_ms\":$(now_ms),\"seg\":\"$1\",\"ev\":\"$2\"${3:+,$3}}" >> "$OUT/marks.jsonl"; }
note() { echo "$(date +%FT%T) $*" >> "$OUT/notes.txt"; log "$*"; }
quiet() { mark "$1" begin; zz "$2"; mark "$1" end; }
# dev_to <file> <cmd...>: a device call under hold10 with its stdout and stderr appended to <file>
dev_to() { local o=$1; shift; if [ -n "$DRY" ]; then hold10 "$@"; else hold10 "$@" >> "$o" 2>&1; fi; }
# launch <out> <tag> <cmd...>: a card launch under hold10; its ENERCAT/SPARSITY result lines, tagged, go to <out>
launch() {
  local o=$1 tag=$2; shift 2
  if [ -n "$DRY" ]; then hold10 "$@"; return 0; fi
  hold10 "$@" 2>> "$OUT/launch.err" | sed -n "s/^\(ENERCAT\|SPARSITY\) /$tag \1 /p" >> "$o"
}
sptrace() { dev_to "$OUT/mgmt.log" "$ETTELEM" sptrace "$1"; }
wait_sampler() {   # wait up to $1 s for the running sampler to finish its --seconds, then collect it
  local i
  for i in $(seq 1 $(( $1 * 10 ))); do
    [ -n "${SAMPLER_PID:-}" ] && kill -0 "$SAMPLER_PID" 2>/dev/null || break
    sleep 0.1
  done
  stop_sampler
}
RESET_USED=; DEBUG_ON=
restore() {        # safe to call twice: sampler off, SP stats trace on, SP log level back to INFO
  stop_sampler
  if [ -n "$RESET_USED" ]; then dev_to "$OUT/mgmt.log" "$DEVMNGT" -n 0 -t SPST:enable; RESET_USED=; fi
  if [ -n "$DEBUG_ON" ]; then dev_to "$OUT/mgmt.log" "$ETTELEM" loglevel info; DEBUG_ON=; fi
}
trap 'restore' EXIT
trap 'exit 143' TERM INT
abort() { note "ABORT: $1"; restore; block_end fail "$1"; exit 1; }
bail_if_others() { others_present || return 0; note "another user appeared before $1"; restore; block_end fail "other user before $1"; exit 3; }
start_or_abort() { start_sampler "$@" || abort "sampler failed to start ($1)"; }

spst_enable() { mark SPSTEN begin; dev_to "$OUT/mgmt.log" "$DEVMNGT" -n 0 -t SPST:enable; mark SPSTEN end; }
spst_extract() {   # $1 label; the extract lands in trace/, renamed <t_end>-<label>-<name>.done, listed in extracts.jsonl
  local t0 t1 f nf info
  t0=$(now_ms); mark "X_$1" begin
  if [ -n "$DRY" ]; then hold10 "$DEVMNGT" -n 0 -t SPST:extract
  else (cd "$OUT/trace" && hold10 "$DEVMNGT" -n 0 -t SPST:extract >> "$OUT/mgmt.log" 2>&1); fi
  t1=$(now_ms); mark "X_$1" end
  for f in "$OUT"/trace/dev0_sp_stats*; do
    [ -e "$f" ] || continue
    case "$f" in *.done) continue ;; esac
    nf="$OUT/trace/$t1-$1-$(basename "$f").done"
    mv "$f" "$nf"
    info=$(python3 "$TEL/tel_util.py" spst-info "$nf")
    echo "{\"label\":\"$1\",\"t_begin_ms\":$t0,\"t_end_ms\":$t1,\"file\":\"$(basename "$nf")\",\"info\":$info}" >> "$OUT/trace/extracts.jsonl"
  done
}
wrap_guard() {     # $1 next arm, $2 its length (s): if the SP stats ring may wrap inside it, let it wrap in quiet first
  local w why
  [ -n "$SMOKE" ] && return 0                              # the smoke check keeps to its 60 s; a lost wrap costs nothing there
  read -r w why < <(python3 "$TEL/tel_util.py" wrapwait "$OUT/trace/extracts.jsonl" "$(now_ms)" "$2")
  [ "${w:-0}" -gt 0 ] 2>/dev/null || return 0
  note "wrap guard before $1: $why"
  quiet "W_$1" "$w"
  spst_extract "W_$1"
}
power_poll() {     # <out.csv> <seconds|0> <interval s> <max iterations|0>: one DM_CMD_GET_MODULE_POWER per call, bounded
  local out=$1 secs=$2 iv=$3 max=$4 i=0 end t w tmp="$OUT/.poll.tmp"
  end=$(( $(now_ms) + secs * 1000 ))
  echo "epoch_ms,watts" > "$out"
  while :; do
    [ "$secs" -gt 0 ] && [ "$(now_ms)" -ge "$end" ] && break
    [ "$max" -gt 0 ] && [ "$i" -ge "$max" ] && break
    i=$((i + 1)); t=$(now_ms); : > "$tmp"
    dev_to "$tmp" "$DEVMNGT" -m DM_CMD_GET_MODULE_POWER -n 0 -u 2000
    w=$(sed -n 's/.*Module Power Output: \([0-9.]*\) W.*/\1/p' "$tmp")
    [ -n "$w" ] && echo "$t,$w" >> "$out"
    if [ -n "$DRY" ] && [ "$i" -ge 2 ]; then echo "DRY (poll loop continues: ${secs}s / ${max} calls, ${iv}s apart)" >&2; break; fi
    [ "$iv" = 0 ] || sleep "$iv"
  done
  rm -f "$tmp"; echo "$i" > "$out.calls"
}
volt_poll() {      # <seconds>: DM_CMD_GET_MODULE_VOLTAGE 80 ms apart, bounded by time checked before each call
  local end i=0; end=$(( $(now_ms) + $1 * 1000 ))
  while [ "$(now_ms)" -lt "$end" ]; do
    i=$((i + 1)); echo "T $(now_ms)" >> "$OUT/volt.log"
    dev_to "$OUT/volt.log" "$DEVMNGT" -m DM_CMD_GET_MODULE_VOLTAGE -n 0 -u 2000
    if [ -n "$DRY" ] && [ "$i" -ge 2 ]; then echo "DRY (voltage loop continues for $1 s, 80 ms apart)" >&2; break; fi
    sleep 0.08
  done
}
sampler_arm() {    # <name> <seconds> <every-ms>: an ettelem arm, its segment marked by the sampler's own run
  local f; f="$OUT/$(echo "$1" | tr 'A-Z' 'a-z').jsonl"
  mark "$1" begin
  start_or_abort "$f" "$2" --every-ms "$3"
  wait_sampler $(( $2 + 20 ))
  mark "$1" end
}
run_arm() {
  case "$1" in
    Q)    quiet Q "$QARM" ;;
    PWR)  mark PWR begin; power_poll "$OUT/pwr.csv" "$PWR_S" 0 0; mark PWR end ;;
    L10)  mark L10 begin; power_poll "$OUT/l10.csv" 0 0.1 "$L10_N"; mark L10 end ;;
    E10)  sampler_arm E10 "$E10_S" 100 ;;
    E20)  sampler_arm E20 "$E20_S" 50 ;;
    E40)  sampler_arm E40 "$E40_S" 25 ;;
    VOLT) mark VOLT begin; volt_poll "$VOLT_S"; mark VOLT end ;;
  esac
}
arm_len() { case "$1" in Q) echo "$QARM" ;; PWR) echo "$PWR_S" ;; L10) echo $(( L10_N * 15 / 100 + 5 )) ;;
  E10) echo "$E10_S" ;; E20) echo "$E20_S" ;; E40) echo "$E40_S" ;; VOLT) echo "$VOLT_S" ;; esac; }
heat_a2() {        # aifoundry2 only, full passes only: heat_to 76 with its curve and marks
  [ "$CARD" = aifoundry2 ] && [ -z "$SMOKE" ] || return 0
  mark "HEAT$1" begin; heat_to 76 "$OUT/heat$1.jsonl" || note "heat_to 76 gave up (phase $1)"; mark "HEAT$1" end
}
fma() {            # fma <values> <seconds> <seed> [budget]: the sparsity_host fma launch of the plan
  echo "$SPARSITY" --test fma --type fp32 --pattern none --values "$1" --shires 0xffffffff --per-shire 32 \
       --seconds "$2" ${4:+--budget "$4"} --seed "$3"
}

# etcfg (a read-only ioctl on /dev/et0_mgmt) is a source file: compile it once per host, outside the data tree
ETCFG=$V3_ROOT/build/claims-v3-bin/etcfg
if [ ! -x "$ETCFG" ]; then
  if [ -n "$DRY" ]; then echo "DRY gcc -O2 -I/opt/et/include -o $ETCFG tools/etcfg/etcfg.c" >&2
  else mkdir -p "$(dirname "$ETCFG")"; gcc -O2 -I/opt/et/include -o "$ETCFG" tools/etcfg/etcfg.c || abort "etcfg did not compile"; fi
fi

ORDER=$(python3 "$TEL/tel_util.py" order $(( CARDN * 100 + PASS )))
echo "{\"seed\":$(( CARDN * 100 + PASS )),\"order\":\"$ORDER\"}" > "$OUT/arms_order.json"
note "pass $PASS on $CARD, arm order: $ORDER${SMOKE:+ (smoke)}"

# ---- phase 1: governor readouts (INFO level, no sampler)
mark GOV begin
dev_to "$OUT/mgmt.log" "$ETTELEM" loglevel info          # a previous interrupted block may have left DEBUG on
if [ "$CARD" = aifoundry2 ] && [ -z "$SMOKE" ] && { [ -z "${BLOCK_C0:-}" ] || [ "$BLOCK_C0" -lt 68 ]; }; then
  heat_a2 0                                                # the plan's rule: aifoundry2 readouts on a die >= 68 C
fi
echo "${BLOCK_C0:-}" > "$OUT/gov/die_block_start.txt"
[ -e "$OUT/heat0.jsonl" ] && tail -1 "$OUT/heat0.jsonl" > "$OUT/gov/die_after_heat.json"
sptrace "$OUT/gov/sp0.bin"
dev_to "$OUT/gov/driver.json" "$ETCFG" /dev/et0_mgmt
for i in $(seq 1 "$GOV_N"); do
  launch "$OUT/gov/runs.jsonl" "G$i" $(fma zeros "$GOV_S" 1 5)
  [ "$i" -lt "$GOV_N" ] && zz 3
done
zz 1
sptrace "$OUT/gov/sp1.bin"                                 # after the launches, before any config query
dev_to "$OUT/gov/config.json" "$ETTELEM" config
dev_to "$OUT/gov/fw.txt" "$DEVMNGT" -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 -u 5000
mark GOV end

# ---- phase 2: the arms
heat_a2 1
spst_enable
spst_extract X0
quiet Q0 "$Q0"
for arm in $ORDER; do
  wrap_guard "$arm" "$(arm_len "$arm")"
  run_arm "$arm"
  [ -z "$SMOKE" ] && spst_extract "$arm"                  # the smoke check extracts once, after the last arm
  quiet "G_$arm" "$GAP"
done
[ -n "$SMOKE" ] && spst_extract ARMS

# ---- phase 3: the --reset-ms segment with three enercat bursts
bail_if_others "the reset segment"
heat_a2 2
mark R begin
RESET_USED=1                                               # set first: a failed start's attempts reset the stats too
start_or_abort "$OUT/reset.jsonl" $(( R_PRE + R_N * (R_BURST + 8) + (R_N - 1) * R_GAP + R_POST + 10 )) --reset-ms 1000
zz "$R_PRE"
for b in $(seq 1 "$R_N"); do
  mark "B$b" begin
  launch "$OUT/burst.jsonl" "B$b" "$ENERCAT" --pattern fmadd_ps --operands random --harts 2 --seconds "$R_BURST" --budget 8
  mark "B$b" end
  [ "$b" -lt "$R_N" ] && zz "$R_GAP"
done
zz "$R_POST"                                               # >= 8 s of 1 s windows after the last burst (P6)
stop_sampler
mark R end
spst_enable; RESET_USED=
spst_extract R

# ---- phase 4: DEBUG block (X2 captures, X3 windows)
bail_if_others "the DEBUG block"
heat_a2 3                                                  # a no-op when the die is still >= 76 C
dev_to "$OUT/mgmt.log" "$ETTELEM" loglevel debug; DEBUG_ON=1
mark DEBUG begin
zz 2                                                       # a full SP pass at DEBUG in the 8 KB ring
sptrace "$OUT/dbg/x2-idle.bin"
if [ "$X2_S" -gt 0 ]; then
  mark X2 begin
  launch "$OUT/dbg/runs.jsonl" X2 $(fma randn "$X2_S" "$PASS") &
  LPID=$!
  zz "$X2_AT"
  sptrace "$OUT/dbg/x2-load.bin"                           # during the burst (Q4)
  wait "$LPID"
  mark X2 end
  zz "$X2_AFTER"
  sptrace "$OUT/dbg/x2-after.bin"
fi
for k in $(seq 1 $(( W_N + W_IDLE ))); do
  mark "W$k" begin
  RESET_USED=1
  start_or_abort "$OUT/dbg/x3-w$k.jsonl" "$W_S" --reset-ms 600000
  if [ "$k" -le "$W_N" ]; then
    zz "$W_AT"
    launch "$OUT/dbg/runs.jsonl" "W$k" $(fma randn "$W_BURST" "$k")
  fi
  wait_sampler $(( W_S + 20 ))
  mark "W$k" end
  sptrace "$OUT/dbg/x3-w$k.bin"                            # right after the window's last sample (R6)
  [ "$k" -lt $(( W_N + W_IDLE )) ] && zz "$W_GAP"
done
mark DEBUG end
dev_to "$OUT/mgmt.log" "$ETTELEM" loglevel info; DEBUG_ON=
spst_enable; RESET_USED=

# ---- pack: one merged SP stats file, gzip the telemetry, a check of what the pass holds
python3 "$TEL/tel_util.py" merge-spst "$OUT/trace" >> "$OUT/notes.txt" 2>&1
rm -f "$OUT/trace/dev0_traces.txt"                         # dev_mngt_service's text decode of the extracts: merged.spst has it all
for f in "$OUT"/*.jsonl "$OUT"/*.csv "$OUT"/volt.log "$OUT"/mgmt.log "$OUT"/dbg/*.jsonl "$OUT"/trace/merged.spst; do
  case "$(basename "$f")" in marks.jsonl|arms_order.json) continue ;; esac
  [ -s "$f" ] && gzip -f "$f"
done
python3 "$TEL/tel_util.py" check "$OUT" ${SMOKE:+--smoke} > "$OUT/check.json"; rc=$?
missing=$(python3 -c 'import json,sys; print(" ".join(json.load(open(sys.argv[1])).get("missing", [])))' "$OUT/check.json" 2>/dev/null)
if [ -n "$DRY" ]; then block_end ok "dry run"; exit 0; fi
if [ -n "$SMOKE" ] && [ "$rc" -ne 0 ]; then block_end fail "smoke: nothing from: $missing"; exit 1; fi
block_end ok "${missing:+missing: $missing}"
