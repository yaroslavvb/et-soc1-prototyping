#!/usr/bin/env bash
# E186 (Q158, the kit; tools/claims-v3/e186/E186.md section 7): one block on aifoundry3 card 0 - a train (one registered pair's A B B A
# processes between its anchors), a fallback kinds pass of E186's 15 kinds, the smoke or the stop-path test - as a lib.sh block. A copy of
# tools/claims-v3/e182/block_e182.sh (E182, run on this card on 8 Nov 2026), itself E178's, with these changes, each marked E186:
#   1. it runs tools/claims-v3/e186/run_e186.py (run_e78.py unchanged, with E186's items and registered fallback order installed, E178's
#      live stops and in-run watcher: board_w >= 65 W or minshire[0] >= 70 C) and, for a train, tools/claims-v3/e186/run_e186t.py; every
#      tile is checked against its registered sha256 first;
#   2. the block number sets the mode: 18610-18619 a train (plan-e186.json's ten: the format's zeros and random anchor as E78 runs into
#      <block>/a0, the train's processes into <block>, the two anchors reversed into <block>/a1; one sampler and one C log for the block;
#      int8 trains open with int8.zeros and int8.full, fp32 with fp32.zeros and fp32.randn, fp16 with fp16.zeros and fp16.randn);
#      18620-18629 a fallback kinds pass (plan-e186.json holds 18620-18624: 35 runs, the tie twice, E78's six anchors three times, each of
#      the 15 kinds once; E78's protocol, heat to 59 C, launch at 58 C after 2.0 s quiet, two burn-ins);
#   3. THE C CHECK (E178's change 3, E182's): every launch runs through tools/claims-v3/ccheck/sparsity_ccheck.sh; the kinds runs with the
#      C-logging host build/ccheck/b/host/sparsity_host, the train processes with E186's train host build/e186host/b/host/sparsity_host
#      (CCHECK_HOST, set for run_e186t.py only); both with the power passes' kernel; CCHECK_LOG is the block's c-log.jsonl;
#   4. --smoke runs e186_common.SMOKE_ITEMS, 2 s each, no preheat, then two processes of H16's train (run_e186t.py --block 18601
#      --processes 2) when E186_TRAINS is not "no"; --stoptest runs no launch at all (E178's);
#   5. aifoundry3 card 0 only (CARD aifoundry3, no V3_DEVICE, the lock etsoc-shire0.lock); run_e78.py's own die cap --max-c 70;
#   6. CARE WITH DEVICE COMMANDS (the owner's rule of Mon 2 Nov 2026), E178's change 6 unchanged: every telemetry call goes through
#      tools/claims-v3/e128/ettelem_guard.sh, and lib.sh's drain_mgmt is replaced by a refusal;
#   7. gen.sha256 covers kinds.json, the merged list, E186's plan and every tile it runs; binaries.sha256 records every binary, the train
#      host and its patched source among them, and the wrapper; e186-code.sha256 names E186's files and E182's files the box calls;
#   8. (new in E186, for the exact copy-back) when the session's E186_T0 is set, the block appends its directory to the session's list
#      build/e186/T<T0>/blocks.txt, which session_e186.sh's manifest reads.
# Everything else - the config reads under timeout 10 at both ends, the card lock, timeout 10 on every device process, the other-user
# test (D1: an idle login does not block on aifoundry3), the sampler (no --reset-ms), the STOP file - is block_e182.sh's, unchanged.
# Nothing is set. Device commands: E186.md section 7, "Device commands".
#
#   bash tools/claims-v3/e186/block_e186.sh <block> [--smoke|--stoptest]
#   V3_DRY=1 bash tools/claims-v3/e186/block_e186.sh <block>          # print every device call, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh                                                  # E186 change 6
drain_mgmt() { log "E186: drain refused: dev_mngt_service is not in E186's classified command list"; return 0; }   # E186 change 6
# Departure D1 (hl/README.md, kept by E60-E171): on aifoundry1 and aifoundry3 a user who is only logged in does not block (other lab
# users keep idle tmux logins there); another user on THIS card does, and so does any other user's device process. Fails closed when
# et-holders is unreadable.
case "$CARD" in aifoundry3|aifoundry1-c*)
  if [ -z "${V3_DRY:-}" ]; then
  others_present() {
    local procs= holders= out n=${V3_DEVICE:-0}
    if [ -z "${V3_DEVICE:-}" ]; then
      procs=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {print $1":"$2":"$3}' | tr '\n' ' ')
    fi
    out=$(sudo -n /usr/local/sbin/et-holders 9>&- 8>&- 2>&1) || { log "others present: et-holders unreadable: ${out:0:120}"; return 0; }
    holders=$(printf '%s\n' "$out" | grep -v 'et-holders' |
              awk -v me="$USER" -v d="/dev/et${n}_" -v l="lock:etsoc-shire${n}.lock" \
                  'index($1, d) == 1 || $1 == l { if ($2 != me && $2 != "") print $2":"$3 }' | tr '\n' ' ')
    if [ -n "${procs// /}${holders// /}" ]; then log "others present: procs=[$procs] holders=[$holders]"; return 0; fi
    return 1
  }
  fi ;;
esac
[ "$CARD" = aifoundry3 ] && [ -z "${V3_DEVICE:-}" ] || { echo "E186's kit runs on aifoundry3 card 0 only (no V3_DEVICE; this is $CARD)" >&2; exit 2; }   # E186 change 5
others_present && exit 3
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block_e186.sh <block> [--smoke|--stoptest]}
MODE=; case "${2:-}" in --smoke) MODE=smoke ;; --stoptest) MODE=stoptest ;; '') ;; *) echo "unknown option ${2}" >&2; exit 2 ;; esac
case "$PASS" in ''|*[!0-9]*) echo "block must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/kinds
E=tools/claims-v3/e186
CC=tools/claims-v3/ccheck                                                                   # E186 change 3
MEAS=$CC/sparsity_ccheck.sh; CCHOST=build/ccheck/b/host/sparsity_host; KERNEL=build/sparsity/kernel/sparsity.elf
TRHOST=build/e186host/b/host/sparsity_host
TARGET=${E78_TARGET:-58}; PREHEAT=${E78_PREHEAT:-59}; BURNIN=${E78_BURNIN:-2}; MAXC=${E78_MAX_C:-70}                       # E186 change 5
QUIET=${E78_QUIET:-2.0}; TIERS=${E78_TIERS:-1,2}; FMA_S=4; EXPN=${E78_EXPN:-e186}; KIND=
ITEMS_ARG=()
TRAINS=${E186_TRAINS:-yes}
if [ -n "$MODE" ]; then
  PREHEAT=0; TARGET=200; QUIET=0.2; FMA_S=2; BURNIN=0; EXPN=${E78_EXPN:-e186}-$MODE; KIND=$MODE                              # E186 change 4
  ITEMS_ARG=(--items "$(python3 -B -c 'import sys; sys.path.insert(0, sys.argv[1]); import e186_common as e; print(",".join(e.SMOKE_ITEMS))' "$E")")
else
  case "$PASS" in                                                                                                            # E186 change 2
    1862[0-9]) KIND=kinds ;;
    1861[0-9]) KIND=train; BURNIN=0
               ANCH=$(python3 -B -c 'import sys; sys.path.insert(0, sys.argv[1]); import e186_common as e; t = e.train_of_block(int(sys.argv[2])); print(",".join(t["anchors_open"]) + " " + ",".join(t["anchors_close"]))' "$E" "$PASS") || { echo "no train for block $PASS" >&2; exit 2; }
               A_OPEN=${ANCH% *}; A_CLOSE=${ANCH#* } ;;
    *) echo "block $PASS is no E186 block on aifoundry3 (trains 18610-18619, fallback kinds passes 18620-18629; the plan holds 18620-18624)" >&2; exit 2 ;;
  esac
fi
log "E186 block $PASS ($KIND): target $TARGET preheat $PREHEAT quiet $QUIET burnin $BURNIN fma $FMA_S s, die cap $MAXC C"

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$HERE/kinds.json" ] || pf+=("no $HERE/kinds.json")
for f in E186.md SHA256SUMS-e186-registration plan-e186.json plan_e186.py harness-e186.json; do
  [ -f "$E/$f" ] || pf+=("no $E/$f"); done                                                                                   # E186 change 1
[ -f tools/claims-v3/m12/kinds-m12-e186.json ] || pf+=("no tools/claims-v3/m12/kinds-m12-e186.json (the merged list)")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY")
[ -x "$HEATER" ] || pf+=("missing heater $HEATER")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -x build/ettelem/ettelem ] || pf+=("missing build/ettelem/ettelem")
[ -x "$MEAS" ] || pf+=("missing the C-check wrapper $MEAS")                                      # E186 change 3
[ -x "$CCHOST" ] || pf+=("missing the C-logging host $CCHOST (tools/claims-v3/ccheck/build_host_ccheck.sh)")
[ -f "$KERNEL" ] || pf+=("missing the kernel $KERNEL")
NEED_TR=; { [ "$KIND" = train ] || { [ "$MODE" = smoke ] && [ "$TRAINS" != no ]; }; } && NEED_TR=1
[ -n "$NEED_TR" ] && { [ -x "$TRHOST" ] || pf+=("missing the train host $TRHOST (tools/claims-v3/e186/build_host_e186.sh, the runbook's step 6)"); }
for b in "$SPARSITY" "$CCHOST"; do
  [ -x "$b" ] || continue
  for s in 'file:' int8 fp16 '--dump-tiles'; do
    grep -a -q -- "$s" "$b" || pf+=("$b has no $s")
  done
done
if [ -x "$CCHOST" ]; then for s in '--c-log' '--c-poison'; do grep -a -q -- "$s" "$CCHOST" || pf+=("$CCHOST has no $s"); done; fi
if [ -n "$NEED_TR" ] && [ -x "$TRHOST" ]; then for s in '--c-log' '--c-poison' '--values-b' '--abba' '--launches' fp16; do grep -a -q -- "$s" "$TRHOST" || pf+=("$TRHOST has no $s"); done; fi   # E186: fp16 too (H16)
for b in "$SPARSITY" "$HEATER" "$CCHOST"; do [ -x "$b" ] && { grep -a -q -- '--stop-file' "$b" || pf+=("$b has no --stop-file"); }; done
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
mkdir -p "$V3_ROOT/build"
if [ "$KIND" = train ]; then LISTITEMS=(--items "$A_OPEN,$A_CLOSE"); LBLK=$PASS; else LISTITEMS=(${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"}); LBLK=$PASS; fi
# E186 change 1: run_e186.py (run_e78.py unchanged, E186's items and registered order, the live stops) in the preflight and the block
LIST=$(python3 -B "$E/run_e186.py" /dev/null --root "$V3_ROOT" --first-block "$LBLK" --tiers "$TIERS" --card "$CARD" \
       --fma-s "$FMA_S" --burnin "$BURNIN" ${LISTITEMS[@]+"${LISTITEMS[@]}"} --list 2>"$V3_ROOT/build/e186-list.err") ||
  pf+=("run_e186 --list (tiles against their sha256, the order against plan-e186.json): $(tail -c 300 "$V3_ROOT/build/e186-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e186 --list output: ${LIST:0:200}") ;; esac
TB=; [ "$KIND" = train ] && TB=$PASS; [ "$MODE" = smoke ] && [ "$TRAINS" != no ] && TB=$PASS
TRS=0
if [ -n "$TB" ]; then
  TL=$(python3 -B "$E/run_e186t.py" /dev/null --root "$V3_ROOT" --block "$TB" ${MODE:+--processes 2} --list 2>"$V3_ROOT/build/e186t-list.err") ||
    pf+=("run_e186t --list: $(tail -c 300 "$V3_ROOT/build/e186t-list.err") ${TL:0:300}")
  TRS=$(python3 -c 'import json,sys; print(int(json.loads(sys.argv[1])["est_s"]) + 1)' "$TL" 2>/dev/null)
  case "$TRS" in ''|*[!0-9]*) pf+=("bad run_e186t --list output: ${TL:0:200}"); TRS=0 ;; esac
fi
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
if [ -n "${E186_T0:-}" ] && [ -z "${V3_DRY:-}" ] && [ -d "build/e186/T$E186_T0" ]; then                                    # E186 change 8
  echo "${OUT#$V3_ROOT/}" >> "build/e186/T$E186_T0/blocks.txt"
fi
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true      # sysfs and files only; it never opens /dev/et*
( sha256sum $HERE/kinds.json tools/claims-v3/m12/kinds-m12-e186.json $E/plan-e186.json tools/claims-v3/m12/tiles/*/*.bin $HERE/tiles/*/*.bin ) \
  > "$OUT/gen.sha256" 2>/dev/null || true                                                                                     # E186 change 7
sha256sum "$E"/*.py "$E"/*.sh "$E"/*.json "$E"/E186.md tools/claims-v3/e182/patch_host_e182.py tools/claims-v3/e182/check_inputs_e182.py \
  "$CC"/*.sh "$CC"/*.py tools/claims-v3/hpl/watcher_q142s.py tools/claims-v3/hpl/run_hpl.py.dated-note.md \
  tools/claims-v3/hpl/run_hpl.py.dated-note-2.md > "$OUT/e186-code.sha256" 2>/dev/null || true
echo "watcher: the kinds watcher of $E/run_e186.py (sha256 $(sha256sum "$E/run_e186.py" 2>/dev/null | cut -c1-64)), also the train runner's" >> "$OUT/e186-code.sha256"
sha256sum "$SPARSITY" "$HEATER" "$CCHOST" "$MEAS" "$KERNEL" build/ettelem/ettelem "$ETTELEM" > "$OUT/binaries.sha256" 2>/dev/null || true   # E186 change 7
[ -n "$NEED_TR" ] && { sha256sum "$TRHOST" build/e186host/src/host/main.cpp >> "$OUT/binaries.sha256" 2>/dev/null || true; }
export CCHECK_LOG="$OUT/c-log.jsonl"                                                                                          # E186 change 3
# The card's static configuration, read only (TDP, threshold, clock, voltage), inside the lock, under timeout 10. `ettelem config`
# has no setter, and the guard admits `config` with no argument only.
card_config() {
  if [ -n "${V3_DRY:-}" ]; then echo "DRY ettelem config" >&2; echo '{"dry":true}'; return 0; fi
  timeout 10 "$ETTELEM" config 2>/dev/null < /dev/null | grep '^{' | tail -1 || true
}
card_config > "$OUT/config_start.json"
start_sampler "$OUT/telemetry.jsonl" $((MAXS + TRS + 900)) || { block_end failed "sampler did not start"; exit 4; }
sleep 3
RUNNER=
on_signal() { [ -n "$RUNNER" ] && kill -TERM "$RUNNER" 2>/dev/null; wait "$RUNNER" 2>/dev/null; stop_sampler; block_end failed "signal"; exit 1; }
trap on_signal TERM INT HUP
run_pass() {   # run_pass <out dir> [run_e186.py's extra arguments]
  local o=$1; shift
  mkdir -p "$o"
  python3 -B "$E/run_e186.py" "$o" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" \
    --heater "$HEATER" --sparsity "$MEAS" --first-block "$PASS" --seed "$PASS" --tiers "$TIERS" \
    --target "$TARGET" --preheat "$PREHEAT" --quiet-s "$QUIET" --max-c "$MAXC" --fma-s "$FMA_S" --burnin "$BURNIN" \
    --card "$CARD" --shires "${E78_SHIRES:-0xffffffff}" --per-shire "${E78_PER_SHIRE:-32}" "$@" &
  RUNNER=$!
  wait "$RUNNER"; rc=$?
  RUNNER=
}
run_train() {  # run_train <out dir> [--processes N]: the train's processes, through the wrapper with the train host (E186 change 3)
  local o=$1; shift
  mkdir -p "$o"
  CCHECK_HOST="$V3_ROOT/$TRHOST" python3 -B "$E/run_e186t.py" "$o" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" \
    --block "$PASS" --sparsity "$MEAS" --card "$CARD" "$@" &
  RUNNER=$!
  wait "$RUNNER"; rc=$?
  RUNNER=
}
if [ "$MODE" = stoptest ]; then                                                                                               # E186 change 4
  st=()
  for k in die board watch; do
    export E186_STOPTEST=$k
    run_pass "$OUT" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"}
    st+=("$k:rc=$rc")
    log "E186 stop-path test ($k): run_e186 exit $rc"
    unset E186_STOPTEST
    # run_e78 refuses to start while its STOP file exists (EXIT_STOP), so each test's STOP line is kept under its own name
    [ -e "$OUT/STOP" ] && mv "$OUT/STOP" "$OUT/STOP.$k"
    sleep 1
  done
  rc=0
  for x in "${st[@]}"; do [ "${x#*:}" = rc=6 ] || rc=1; done
  printf '%s\n' "${st[@]}" > "$OUT/stoptest.rc"
elif [ "$MODE" = smoke ]; then
  run_pass "$OUT" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"}
  if [ "$rc" -eq 0 ] && [ "$TRAINS" != no ]; then
    run_train "$OUT/train" --processes 2
    trc=$rc
    log "E186 smoke: the train's two processes, run_e186t exit $trc"
    echo "$trc" > "$OUT/train.rc"
    rc=0                                   # the gate reads the train items; the kinds smoke passed
  fi
elif [ "$KIND" = train ]; then
  run_pass "$OUT/a0" --items "$A_OPEN"
  log "E186 train $PASS: opening anchors $A_OPEN, run_e186 exit $rc"
  if [ "$rc" -eq 0 ]; then
    run_train "$OUT"
    log "E186 train $PASS: the train's processes, run_e186t exit $rc"
    if [ "$rc" -eq 0 ]; then
      run_pass "$OUT/a1" --items "$A_CLOSE"
      log "E186 train $PASS: closing anchors $A_CLOSE, run_e186 exit $rc"
    fi
  fi
else
  run_pass "$OUT"
fi
sleep 5
stop_sampler
card_config > "$OUT/config_end.json"
[ -s "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
# c-log.jsonl stays as written (ccheck.py reads it as text at the desk; collect_e186.sh gzips the committed copy, once: kit v5)
case $rc in
  0) block_end ok "pass $PASS ($KIND)" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "run_e186 or run_e186t exit $rc ($KIND)"; exit 1 ;;
esac
