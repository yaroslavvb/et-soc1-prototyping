#!/usr/bin/env bash
# PCIE2 (hub rungs 34 and 35): one pass on the local card. README.md has the design, PREREG.md the predictions.
#
#   bash tools/claims-v3/pcie2/block.sh <pass>            1-99 validation (only once frozen: LOCK.sha256 verifies),
#                                                         100-899 development, 900+ a smoke (three short processes)
#   V3_DRY=1 bash tools/claims-v3/pcie2/block.sh <pass>   no device, no card lock, no et-who: pcie2lib.py's stub
#   bash tools/claims-v3/pcie2/block.sh --preflight <pass>   the file checks only (binaries, hashes, ET_DEVICES, the
#                                                         freeze), no device and no et-who: prints them, exit 0 or 2
#   bash tools/claims-v3/pcie2/block.sh --binhash         the probe's and kernels' hashes (files only), for the freeze
#   aifoundry1: V3_DEVICE=1 (card 1; lib.sh exports ET_DEVICES=1). Card 0 is refused. aifoundry2 is refused unless
#   PCIE2_ALLOW_AIFOUNDRY2=1 (its card runs the frozen DV2 validation until about 17:00 PDT, 29 September).
#
# A pass: a 1 s telemetry sample; ten device processes of workloads/pciebench's probe in an order shuffled per pass
# (pcie2lib.py plan): nine `--test conc` (R35: 2 commands of 1, 4, 16, 64 MB, one and two in flight, plain and in 8
# DMA elements) and one `--test touch` (R34: the first touch after a host copy, in kernels launched without the L3
# flush); a sample after the fifth process and one at the end. About 25 s of card time, 40 s of wall time.
#
# Rules this script enforces (the task's card etiquette, AGENT.md section 5):
#  - before every device-opening process (the samples included): lib's others_present and ours_running, and
#    `et-who --check` (any holder, or a failed check, stops the pass: exit 3, which the queue retries later). The
#    check sees every card of the host, so on aifoundry1 anyone on card 0 defers a card-1 pass too (conservative);
#  - each device-opening process holds the card lock alone: `flock -n /run/lock/etsoc-shire<N>.lock` around it, taken
#    without waiting (a held lock stops the pass: exit 3) and released when it exits, never across processes (so this
#    block does not use lib's block_begin, which holds the lock for a whole block); 1 s between processes;
#  - `timeout 10` on each (the probe also stops starting work at --budget 8.5 s);
#  - a probe process that fails stops the pass at once (exit 1): nothing more opens the card. One that looks hung
#    (killed by the timeout: exit 124, 137 or 143; or an output naming a hang: HPSQ, "did not finish", "did not drain",
#    abort) stops it with exit 5 and writes build/claims-v3/STOP, which stops run_passes.sh and queue.sh (never under
#    V3_DRY);
#  - any die >= 90 C in a sample stops the pass (exit 4) and writes build/claims-v3/STOP (never under V3_DRY); a pass
#    whose samples give no die temperature three times running stops too (exit 3);
#  - the binaries must be this tree's: the probe carries the sha256 of the sources it was built from (host/CMakeLists
#    writes them into Constants.h) and every pass refuses a probe whose sources differ from the tree's; once frozen,
#    the kernels' .text must also match TEXT.sha256 (freeze.sh). On aifoundry1 the probe and ettelem must be built
#    against aifoundry1's device layer, the one that honours ET_DEVICES (its name is in the binary; the stock library
#    has none, and a binary built against it would open card 0 as device 0). main.cpp must never contain that name
#    as a string, or this check would pass on any build;
#  - nothing opens card 0 and nothing runs dev_mngt_service (the stock build opens every card's management node);
#  - nothing changes the card: no reset, TDP, clock, firmware or log level.
# Exit: 0 done (or already done), 1 a process failed (block.json "failed"), 2 refused or preflight, 3 someone else (or
# the lock, or no temperature): retry later, 4 hot, 5 a process looked hung (STOP written).
# Data: $DATA_ROOT/pcie2/p<pass>/ (build/claims-v3/<card>/, or build/claims-v3-dry/<card>/ under V3_DRY): plan.json,
# <id>.out/.err per process, launches.jsonl, marks.jsonl, tel-{pre,mid,post}.json, tel.jsonl, manifest.txt,
# code.sha256, binaries.json, pass.json, check.json, block.json.
# DRY knobs: PCIE2_DRY_CARD (the card to act as, e.g. aifoundry1-c1; also with --preflight), PCIE2_DRY_R35 /
# PCIE2_DRY_R34 (the stub's models), PCIE2_DRY_CMD_MS (the stub's per-command fixed cost), PCIE2_DRY_HELD=<step>
# (et-who reports a holder before that step), PCIE2_DRY_TEMP=<C> (the samples' die), PCIE2_DRY_NOTEL=<n> (the first n
# samples give no reading), PCIE2_DRY_FAIL=conc|touch (that process fails, exit 1; PCIE2_DRY_FAILMSG its message),
# PCIE2_DRY_HANG=conc|touch (that process exits 124, as a timeout would).
# Overrides: PCIE2_BIN (the probe), PCIE2_ETTELEM (the sampler).
set -u
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"      # cd's to the tree root; CARD, DATA_ROOT, ETTELEM, ET_DEVICES, log
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE
HERE=tools/claims-v3/pcie2
LIB=$HERE/pcie2lib.py
DRY=${V3_DRY:-}
PREFLIGHT=   # files-only modes (no device, no et-who): --preflight <pass>, --binhash
case "${1:-}" in --preflight) PREFLIGHT=1; shift ;; --binhash) PREFLIGHT=binhash ;; esac
TEL_AFTER=5
BIN=${PCIE2_BIN:-build/pciebench/host/pciebench_host}
ETTELEM=${PCIE2_ETTELEM:-$ETTELEM}
OBJCOPY=/opt/et/bin/riscv64-unknown-elf-objcopy
# never run: lib's drain_mgmt runs the stock dev_mngt_service, which opens every card's management node
drain_mgmt() { log "drain_mgmt skipped: pcie2 never runs dev_mngt_service"; }
if [ -n "$DRY$PREFLIGHT" ] && [ -n "${PCIE2_DRY_CARD:-}" ]; then CARD=$PCIE2_DRY_CARD; fi
[ -n "$DRY" ] && DATA_ROOT=$V3_ROOT/build/claims-v3-dry/$CARD
DEVN=${V3_DEVICE:-0}
case "$CARD" in
  aifoundry1-c0) echo "pcie2: aifoundry1's card 0 is refused (the owner's rule: never card 0)" >&2; exit 2 ;;
  aifoundry1-c1) DEVN=1 ;;
  aifoundry2) if [ -z "$DRY$PREFLIGHT" ] && [ "${PCIE2_ALLOW_AIFOUNDRY2:-}" != 1 ]; then
      echo "pcie2: aifoundry2 is refused until DV2 ends (~17:00 PDT 29 Sep); then PCIE2_ALLOW_AIFOUNDRY2=1" >&2; exit 2; fi ;;
esac

TELF=; EELF=
kernels() {   # the kernel paths compiled into the probe (its Constants.h)
  TELF=$(grep -a -o '/[[:alnum:]/._-]*/touch\.elf' "$BIN" 2>/dev/null | head -1)
  EELF=$(grep -a -o '/[[:alnum:]/._-]*/empty\.elf' "$BIN" 2>/dev/null | head -1)
}
textsha() {   # the sha256 of an ELF's .text (identical code from the three toolchains: AGENT.md section 6)
  [ -x "$OBJCOPY" ] && [ -f "$1" ] || return 1
  "$OBJCOPY" -O binary -j .text "$1" /dev/stdout 2>/dev/null | sha256sum | cut -c1-64
}
SRC_RE='PCIEBENCH_SRC_SHA256 main=[0-9a-f]\{64\} args=[0-9a-f]\{64\} touch=[0-9a-f]\{64\}'
bin_src() { grep -a -o "$SRC_RE" "$BIN" 2>/dev/null | head -1; }   # the sources the probe was built from
tree_src() {  # the same string for this tree's sources
  local a b c
  a=$(sha256sum workloads/pciebench/host/main.cpp | cut -c1-64); b=$(sha256sum workloads/pciebench/touch_args.h | cut -c1-64)
  c=$(sha256sum workloads/pciebench/kernel/touch.c | cut -c1-64)
  echo "PCIEBENCH_SRC_SHA256 main=$a args=$b touch=$c"
}
binhash() {   # JSON: sha256 of the probe and its kernels, the kernels' .text, and the sources the probe was built from
  kernels
  local f h t out="{\"bin\":\"$BIN\",\"src\":\"$(bin_src)\",\"tree_src\":\"$(tree_src)\""
  for f in "$BIN" "$TELF" "$EELF"; do
    [ -n "$f" ] && [ -f "$f" ] || { out="$out,\"${f:-missing}\":null"; continue; }
    h=$(sha256sum "$f" | cut -c1-64); t=
    [ "$f" != "$BIN" ] && t=$(textsha "$f")
    out="$out,\"${f##*/}\":{\"path\":\"$f\",\"sha256\":\"$h\"${t:+,\"text_sha256\":\"$t\"}}"
  done
  echo "$out}"
}
if [ "${1:-}" = --binhash ]; then binhash; exit 0; fi

PASS=${1:?usage: block.sh [--preflight] <pass> | --binhash}
case "$PASS" in ''|*[!0-9]*|0) echo "pcie2: the pass must be a number from 1" >&2; exit 2 ;; esac
KIND=validation; [ "$PASS" -ge 100 ] && KIND=development; [ "$PASS" -ge 900 ] && KIND=smoke
SMOKE=; [ "$KIND" = smoke ] && SMOKE=--smoke

# ---- the freeze: validation passes run only on the frozen code ------------------------------------------------------
FROZEN=false; PREREG_SHA=$(sha256sum "$HERE/PREREG.md" 2>/dev/null | cut -c1-64)
if [ -f "$HERE/LOCK.sha256" ]; then
  if sha256sum -c --quiet "$HERE/LOCK.sha256" > /dev/null 2>&1; then FROZEN=true
  else
    echo "pcie2: LOCK.sha256 does not verify; changed since the freeze:" >&2
    sha256sum -c --quiet "$HERE/LOCK.sha256" 2>&1 | head -20 >&2; exit 2
  fi
fi
if [ "$KIND" = validation ] && [ "$FROZEN" != true ] && [ -z "$DRY" ]; then
  echo "pcie2: validation pass $PASS needs the freeze (README.md, 'The freeze'): no LOCK.sha256" >&2; exit 2
fi

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
preflight_files() {  # the binaries: present, this tree's, ET_DEVICES on aifoundry1, the frozen kernels' .text
  local want got f t w
  kernels
  [ -x "$BIN" ] || { pf+=("no $BIN (scripts/deploy-lab.sh <host> workloads/pciebench)"); return; }
  grep -a -q -- '--touch-mb' "$BIN" 2>/dev/null || pf+=("$BIN has no --touch-mb: a build from before rung 34")
  { [ -n "$TELF" ] && [ -f "$TELF" ]; } || pf+=("the touch kernel ${TELF:-?} compiled into $BIN is missing")
  { [ -n "$EELF" ] && [ -f "$EELF" ]; } || pf+=("the empty kernel ${EELF:-?} compiled into $BIN is missing")
  want=$(tree_src); got=$(bin_src)
  [ "$got" = "$want" ] || pf+=("$BIN was not built from this tree's main.cpp, touch_args.h and touch.c (binary: '${got:-no source hash, a build from before 28 Sep}'; tree: '$want'): rebuild with scripts/deploy-lab.sh <host> workloads/pciebench")
  [ -x "$ETTELEM" ] || pf+=("no $ETTELEM")
  if [ "$CARD" = aifoundry1-c1 ]; then
    for f in "$BIN" "$ETTELEM"; do
      [ -f "$f" ] && ! grep -a -q ET_DEVICES "$f" && pf+=("$f does not honour ET_DEVICES (built against the stock device layer?): it would open card 0 as device 0")
    done
  fi
  if [ "$FROZEN" = true ]; then
    if [ ! -f "$HERE/TEXT.sha256" ]; then pf+=("frozen but no $HERE/TEXT.sha256")
    elif [ ! -x "$OBJCOPY" ]; then pf+=("no $OBJCOPY: the kernels' .text cannot be checked against the freeze")
    else
      for f in "$TELF" "$EELF"; do
        [ -f "$f" ] || continue
        t=$(textsha "$f"); w=$(awk -v n="${f##*/}" '$2 == n {print $1}' "$HERE/TEXT.sha256")
        [ -n "$w" ] && [ "$t" = "$w" ] || pf+=("${f##*/} .text $t differs from the freeze's ${w:-(none)} (TEXT.sha256)")
      done
    fi
  fi
}
if [ -n "$PREFLIGHT" ]; then
  preflight_files
  echo "pcie2 preflight as $CARD, pass $PASS ($KIND, frozen $FROZEN): $BIN, $ETTELEM"
  if [ ${#pf[@]} -eq 0 ]; then echo "preflight ok: $(bin_src)"; exit 0; fi
  for x in "${pf[@]}"; do echo "preflight: $x"; done
  exit 2
fi

OUT=$DATA_ROOT/pcie2/p$PASS
if [ -e "$OUT/block.json" ] && grep -q '"status":"ok"' "$OUT/block.json"; then log "pcie2 p$PASS already done"; exit 0; fi
[ -d "$OUT" ] && mv "$OUT" "$OUT.attempt-$(now_ms)"
mkdir -p "$OUT"
T0=$(now_ms); C_START=null; C_LAST=null; MAXC=0; MHZ=(); NOTEL=0

mark() { echo "{\"t_ms\":$(now_ms),\"what\":\"$1\"${2:+,$2}}" >> "$OUT/marks.jsonl"; }
finish() {  # finish <status> <note>: block.json in lib's block_end format (queue.sh reads "status":"ok")
  local note; note=$(printf '%s' "${2:-}" | tr '\n"\\' " ''")
  printf '{"exp":"pcie2","pass":%s,"card":"%s","kind":"%s","t0_ms":%s,"t1_ms":%s,"die_c_start":%s,"die_c_end":%s,"max_c":%s,"status":"%s","note":"%s","frozen":%s,"dry":%s}\n' \
    "$PASS" "$CARD" "$KIND" "$T0" "$(now_ms)" "$C_START" "$C_LAST" "$MAXC" "$1" "$note" "$FROZEN" \
    "$( [ -n "$DRY" ] && echo true || echo false )" > "$OUT/block.json"
  log "pcie2 p$PASS ends: $1 $note"
}
trap 'finish killed "signal"; exit 3' TERM INT HUP
interrupted() { mark interrupted "\"before\":\"$1\",\"why\":\"$2\""; finish interrupted "before $1: $2"; exit 3; }

python3 "$LIB" plan --pass "$PASS" $SMOKE > "$OUT/plan.jsonl" 2> "$OUT/plan.err" || pf+=("plan: $(head -c 300 "$OUT/plan.err")")
python3 -c 'import json,sys; json.dump([json.loads(l) for l in open(sys.argv[1])], open(sys.argv[2], "w"), indent=1)' \
  "$OUT/plan.jsonl" "$OUT/plan.json" 2>/dev/null || pf+=("plan.json")
if [ -z "$DRY" ]; then
  preflight_files
  command -v flock > /dev/null || pf+=("no flock")
  [ -e "/run/lock/etsoc-shire$DEVN.lock" ] || pf+=("no card lock file /run/lock/etsoc-shire$DEVN.lock")
  if ! command -v et-who > /dev/null; then pf+=("no et-who")
  else et-who --check > /dev/null 2>&1; case $? in 0|1) ;; *) pf+=("et-who --check fails here (needs the 27 September et-who)") ;; esac; fi
  LOCKF=/run/lock/etsoc-shire$DEVN.lock
else
  LOCKF=$OUT/card.lock
fi
if [ ${#pf[@]} -gt 0 ]; then
  for x in "${pf[@]}"; do log "preflight: $x"; done
  finish failed "preflight: ${pf[*]}"; exit 2
fi
{ [ -n "$DRY" ] && echo '{"dry":true}' || binhash; } > "$OUT/binaries.json"
sha256sum tools/claims-v3/lib.sh tools/claims-v3/queue.sh "$HERE"/*.sh "$HERE"/*.py "$HERE"/*.md "$HERE"/*.txt \
  "$HERE"/*.sha256 workloads/pciebench/host/main.cpp workloads/pciebench/kernel/touch.c \
  workloads/pciebench/kernel/empty.c workloads/pciebench/touch_args.h workloads/pciebench/host/CMakeLists.txt \
  workloads/pciebench/host/Constants.h.in > "$OUT/code.sha256" 2>/dev/null || true
if [ -n "$DRY" ]; then echo "DRY: no manifest" > "$OUT/manifest.txt"
else et-lab-manifest > "$OUT/manifest.txt" 2>&1 || true; fi   # sysfs and files only, never a device node
log "pcie2 p$PASS ($KIND${DRY:+, DRY}) begins -> $OUT"

# ---- the card: who is on it, and one process at a time under its lock ------------------------------------------
card_busy() {  # card_busy <step>: true (0) when anyone else is on the card, or the check itself failed
  if others_present || ours_running; then return 0; fi
  if [ -n "$DRY" ]; then
    if [ "${PCIE2_DRY_HELD:-}" = "$1" ]; then log "DRY: et-who --check reports a holder before $1"; return 0; fi
    return 1
  fi
  local out rc
  out=$(et-who --check 2>&1); rc=$?
  [ $rc -eq 0 ] && return 1
  log "et-who --check before $1 (rc $rc): $(printf '%s' "$out" | tr '\n' ';' | cut -c1-300)"
  return 0
}
locked10() {  # locked10 <stdout file> <stderr file> <cmd...>: under the card lock, timeout 10; 75 if the lock is held
  local o=$1 e=$2 rc; shift 2
  exec 7<>"$LOCKF"
  if ! flock -n 7; then exec 7>&-; return 75; fi
  [ -n "$DRY" ] && mark lock_taken "\"file\":\"$LOCKF\""
  timeout 10 "$@" > "$o" 2> "$e" < /dev/null; rc=$?
  exec 7>&-      # released: the process that inherited fd 7 has exited
  return $rc
}
tel() {  # tel <name>: one 1 s sample of this card; the 90 C gate. Three tries (ettelem fails to start 1 time in 3).
  local f=$OUT/tel-$1.json rc s c m try
  for try in 1 2 3; do
    card_busy "tel-$1" && interrupted "tel-$1" "another user or device process"
    if [ -n "$DRY" ]; then
      NOTEL=$((NOTEL + 1))
      if [ "$NOTEL" -le "${PCIE2_DRY_NOTEL:-0}" ]; then locked10 "$f.raw" "$f.err" true
      else
        locked10 "$f.raw" "$f.err" printf '{"dry":true,"temp_c":{"pmic":60,"ioshire":[%s,0,0],"minshire":[%s,0,0]},"mhz":{"minion":600}}\n' \
          "${PCIE2_DRY_TEMP:-80}" "${PCIE2_DRY_TEMP:-80}"
      fi
    else
      locked10 "$f.raw" "$f.err" "$ETTELEM" sample --seconds 1 --every-ms 500
    fi
    rc=$?
    [ $rc -eq 75 ] && interrupted "tel-$1" "the card lock $LOCKF was held"
    grep '^{' "$f.raw" 2>/dev/null | tail -1 > "$f"; rm -f "$f.raw"
    s=$(python3 "$LIB" telsum "$f")
    echo "{\"name\":\"$1\",\"try\":$try,\"rc\":$rc,\"t_ms\":$(now_ms),\"summary\":\"$s\"}" >> "$OUT/tel.jsonl"
    [ "$s" != none ] && break
    log "telemetry $1 try $try: no reading (rc $rc)"
    sleep 2
  done
  [ "$s" = none ] && interrupted "tel-$1" "no die temperature in three samples: the 90 C gate cannot be checked"
  read -r c m <<< "$s"
  MHZ+=("$m"); C_LAST=$c; [ "$C_START" = null ] && C_START=$c; [ "$c" -gt "$MAXC" ] && MAXC=$c
  log "telemetry $1: hottest die $c C, minion $m MHz"
  if [ "$c" -ge 90 ]; then
    mark hot "\"at\":\"$1\",\"c\":$c"
    finish hot "a die read $c C at $1"
    if [ -z "$DRY" ]; then mkdir -p build/claims-v3 && touch build/claims-v3/STOP; log "wrote build/claims-v3/STOP"; fi
    exit 4
  fi
}

# ---- the pass ------------------------------------------------------------------------------------------------------
tel pre
n=0
while IFS=$'\t' read -r id args; do
  card_busy "$id" && interrupted "$id" "another user or device process"
  t0=$(now_ms)
  # shellcheck disable=SC2086  # args are the plan's words, none with spaces
  if [ -n "$DRY" ]; then locked10 "$OUT/$id.out" "$OUT/$id.err" python3 "$LIB" stub $args
  else locked10 "$OUT/$id.out" "$OUT/$id.err" "$BIN" $args; fi
  rc=$?
  [ $rc -eq 75 ] && interrupted "$id" "the card lock $LOCKF was held"
  echo "{\"id\":\"$id\",\"rc\":$rc,\"t0_ms\":$t0,\"t1_ms\":$(now_ms),\"args\":\"$args\"}" >> "$OUT/launches.jsonl"
  log "$id: exit $rc in $(( $(now_ms) - t0 )) ms (the lock released)"
  n=$((n + 1))
  if [ $rc -ne 0 ]; then   # stop at once: nothing more opens the card after a process that failed
    hang=
    case $rc in 124|137|143) hang="killed by the timeout (exit $rc)" ;; esac
    if [ -z "$hang" ] && grep -a -q -E 'HPSQ|did not finish|did not drain|[Aa]bort|[Hh]ang' "$OUT/$id.out" "$OUT/$id.err" 2>/dev/null; then
      hang="exit $rc, and its output names a hang: $(grep -a -h -o -E '.{0,60}(HPSQ|did not finish|did not drain|[Aa]bort|[Hh]ang).{0,40}' "$OUT/$id.out" "$OUT/$id.err" | head -1)"
    fi
    if [ -n "$hang" ]; then
      mark hung "\"id\":\"$id\",\"rc\":$rc"
      finish hung "$id: $hang; the pass stopped after $n processes"
      if [ -z "$DRY" ]; then mkdir -p build/claims-v3 && touch build/claims-v3/STOP; log "wrote build/claims-v3/STOP"
      else log "DRY: would write build/claims-v3/STOP"; fi
      exit 5
    fi
    mark failed "\"id\":\"$id\",\"rc\":$rc"
    finish failed "$id exited $rc; the pass stopped after $n processes"
    exit 1
  fi
  [ "$n" -eq "$TEL_AFTER" ] && tel mid
  sleep 1
done < <(python3 -c 'import json,sys
for x in json.load(open(sys.argv[1])): print(x["id"] + "\t" + " ".join(x["args"]))' "$OUT/plan.json")
tel post

printf '{"card":"%s","pass":%s,"kind":"%s","dry":%s,"frozen":%s,"prereg_sha256":"%s","t0_ms":%s,"t1_ms":%s,"max_c":%s,"mhz":[%s],"processes":%s,"host":"%s"}\n' \
  "$CARD" "$PASS" "$KIND" "$( [ -n "$DRY" ] && echo true || echo false )" "$FROZEN" "$PREREG_SHA" "$T0" "$(now_ms)" \
  "$MAXC" "$(IFS=,; echo "${MHZ[*]}")" "$n" "$(hostname)" > "$OUT/pass.json"
python3 "$HERE/reduce.py" --check-pass "$OUT" > "$OUT/check.json" 2>&1
if grep -q '"ok": true' "$OUT/check.json"; then finish ok "$n processes"; exit 0; fi
finish failed "check: $(head -c 400 "$OUT/check.json")"
exit 1
