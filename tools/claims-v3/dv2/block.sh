#!/usr/bin/env bash
# DV2 on aifoundry2 (DESIGN.md rev 2, PREREG-DEV.md §4; 27-28 Sep 2026): one pass of the development night. queue.sh
# runs it as "dv2 <pass>" (schedule-dv2-aifoundry2.txt); every pass is also runnable alone:
#
#   bash tools/claims-v3/dv2/block.sh <pass>
#   V3_DRY=1 DV2_ANY_TIME=1 HP_DRY_REST=61 bash tools/claims-v3/dv2/block.sh <pass>     no device: the simulator
#
# Passes (README.md):
#   1001-1999  Z1: one read-only watch cycle at its slot (night.json: 00:40 + 10 min x (k - 1)); a slot more than 5 min
#              past is skipped, an early pass waits for its slot. Gate, flock -n on the card lock (the cycle is skipped
#              if it is held), then sptrace, residency 2-6 + uptime, config (the threshold must read 65), one 1 s
#              sample --reset-ms 1000. About 5 s of card time. z1.json: the reading, COOL (<= 64), the governor lines.
#   4001       the smoke (PREREG-DEV row 4): R0, sptrace, Z2, config, one 2 s UNI32@4 launch inside the sampler with
#              the one-shot reset, sptrace, the parser, the post-run clock check, the global-state table.
#   5001       C1m development (row 5): only on LOOP (R0 >= 66) with no Z1 reading <= 64 in the previous 60 min, in
#              the C1m window; 12 runs (4 blocks of INT16@32, PER16@32, UNI32@16 in DESIGN §5.4's rows) from the
#              falling E+1 -> E edge (E = R0 + 2), up to 3 x 7 s launches until the mean reads E + 4; 65 min cap;
#              stops at a reading <= 64.
#   6001-6099  a NAT candidate (row 6): exits at once unless NAT-AUTOSTART exists, the newest Z1 read <= 64 (fresh),
#              no NAT session ran tonight and it is before 07:00. Then: R0 and the branch (NAT-4/3/2/1), the probe
#              (must be ALIVE, else ALERT-PROBE-SILENT and no heat), the smoke, WARNING (O2), ADD, T-blocks in the
#              DESIGN §5.5 cycle (DEV-1/2/3/10 by their rules), 2 RST runs, ADD, the level restored and checked, Z2,
#              the global-state table. <= 60 min of card time, ends by 08:00.
#   7xxx       D1 (the threshold raise): REFUSED. It needs the owner's explicit yes (DESIGN §4.3); this build has no
#              threshold set path at all (ettelem-dv2 refuses 'threshold set').
#
# Exit codes: 0 done or skipped (block.json says which), 1 failed or aborted, 2 refused, 3 someone else on the card.
set -u
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"           # cd's to the tree root
. tools/claims-v3/dv2/dv2lib.sh
PASS=${1:?usage: dv2/block.sh <pass>}
case "$PASS" in
  1[0-9][0-9][0-9]) KIND=Z1 ;;
  40[0-9][0-9]) KIND=SMOKE ;;
  50[0-9][0-9]) KIND=C1M ;;
  60[0-9][0-9]) KIND=NAT ;;
  7[0-9][0-9][0-9]) echo "dv2: pass $PASS is D1 (the threshold raise): refused; it needs the owner's explicit yes (DESIGN §4.3) and this build has no set path" >&2; exit 2 ;;
  *) echo "dv2: unknown pass $PASS (1001-1999 Z1, 4001 smoke, 5001 C1m, 6001-6099 NAT)" >&2; exit 2 ;;
esac
if ! bad=$("${DV2PY[@]}" envcheck); then log "dv2: refused: dry-only variables without V3_DRY: $bad"; exit 2; fi
if [ -n "${DV2_VAL:-}" ]; then   # PREREG-VAL's replication: only a NAT session (6050-6099), only with the frozen files
  case "$PASS" in 60[5-9][0-9]) ;; *) log "dv2: DV2_VAL: pass $PASS is not a validation NAT session (6050-6099): refused"; exit 2 ;; esac
  ( sha256sum -c --quiet tools/claims-v3/dv2v/LOCK.sha256 ) > /dev/null 2>&1 || { log "dv2: DV2_VAL: the files differ from the PREREG-VAL lock: refused"; exit 2; }
  export DV2_NO_WARNING=1          # no log-level change in validation (the SP-line items are not registered)
fi
[ "$bad" = - ] || log "dv2: dry overrides: $bad"
eval "$("${DV2PY[@]}" params | sed 's/^SET //')"
mkdir -p "$DV2_DATA"
if night_stopped; then log "dv2 p$PASS: the night stop is set ($(tail -1 "$DV2_DATA/NIGHT-STOP")): nothing runs"; exit 0; fi
if ! dry; then for b in "$HEATER" "$ETTELEM" "$HEATER_KERNEL"; do [ -e "$b" ] || { log "dv2: missing $b (README: build it first)"; exit 1; }; done; fi
[ -e /run/lock/etsoc-shire0.lock ] || dry || { log "dv2: /run/lock/etsoc-shire0.lock is missing: not starting without the card lock"; exit 1; }
END_BY=$("${DV2PY[@]}" endby)
if [ "$END_BY" != 0 ] && [ "$(now_ms)" -ge "$END_BY" ]; then log "dv2 p$PASS: after the night's end: nothing runs"; exit 0; fi

skip_record() {   # skip_record <why>: a pass that did nothing on the card (queue.sh moves on)
  mkdir -p "$DV2_DATA/p$PASS"
  printf '{"exp":"dv2","pass":%s,"card":"%s","t0_ms":%s,"t1_ms":%s,"status":"skipped","note":%s}\n' "$PASS" "$CARD" \
    "$(now_ms)" "$(now_ms)" "$(jstr "$1")" > "$DV2_DATA/p$PASS/block.json"
  log "dv2 p$PASS skipped: $1"
}
session_json() {  # session_json <launched true|false> <note>
  python3 - "$OUT/session.json" "$KIND" "$PASS" "$1" "$2" "${R0:-}" "${BRANCH:-}" "${PROBE_CLASS:-}" "${SPLINES:-}" \
    "${BLOCKS_DONE:-0}" "${SESSION_T0:-0}" "$(now_ms)" "${LEVEL_CHECK:-}" <<'PY'
import json, sys
f, kind, p, launched, note, r0, br, pc, spl, nb, t0, t1, lc = sys.argv[1:14]
json.dump({"kind": kind, "pass": int(p), "launched": launched == "true", "note": note,
           "r0": int(r0) if r0.lstrip("-").isdigit() else None, "branch": br or None, "probe_class": pc or None,
           "sp_lines_registered": spl == "1", "blocks": int(nb), "t0_ms": int(t0), "t1_ms": int(t1),
           "card_time_s": round((int(t1) - int(t0)) / 1000.0, 1) if int(t0) else None, "level_check": lc or None},
          open(f, "w"), indent=1)
PY
}

# =============================================================================================== Z1 (read-only)
if [ "$KIND" = Z1 ]; then
  SLOT=$("${DV2PY[@]}" slot --pass "$PASS")
  if [ "$SLOT" != 0 ]; then
    now=$(now_ms)
    if [ "$now" -gt $(( SLOT + 300000 )) ]; then skip_record "slot $(date -d @$(( SLOT / 1000 )) +%H:%M) passed"; exit 0; fi
    if [ "$now" -lt "$SLOT" ]; then
      [ $(( SLOT - now )) -gt 3600000 ] && { skip_record "slot more than 60 min ahead: misconfigured"; exit 0; }
      sleep $(( (SLOT - now) / 1000 ))
    fi
  fi
  OUT=$DV2_DATA/p$PASS; mkdir -p "$OUT"; : > "$OUT/marks.jsonl"
  T0=$(now_ms)
  if others_present || ours_running || [ -n "$(foreign_procs)" ] || [ -n "$(etwho_foreign)" ] || [ -n "$(other_framework)" ]; then
    skip_record "gate: another user, device process, holder or framework queue present"; exit 0
  fi
  if ! dry; then exec 9<>/run/lock/etsoc-shire0.lock; flock -n 9 || { skip_record "the card lock is held"; exit 0; }; fi
  mark z1_begin "\"slot_ms\":$SLOT"
  dv2_level_pending_restore          # a WARNING a killed or aborted session left is restored here too
  dv2_sptrace "$OUT/sp.bin"
  dv2_dumpcheck "$OUT/sp.bin" || true
  dv2_z2 "$OUT/z2"
  dv2_config "$OUT/config.json"
  if dry; then "${DV2PY[@]}" dry-sampler --card "$CARD" --out "$OUT/tel.jsonl" --seconds 1 --every-ms 100 --reset-ms 1000
  else hold10 "$ETTELEM" sample --seconds 1 --every-ms 100 --reset-ms 1000 > "$OUT/tel.jsonl" 2>> "$OUT/mgmt.log"; fi
  dry || exec 9>&-
  read -r _ READING _ THR COOL <<< "$("${DV2PY[@]}" z1sum --dir "$OUT" --pass "$PASS")"
  st=ok; note="reading $READING C, threshold $THR${COOL:+, $COOL}"
  if [ "$THR" != 65 ]; then trc=0; dv2_threshold_ok "$OUT/config.json" || trc=$?
    case "$trc" in 1) st=fail; note="$note: THRESHOLD ALERT" ;; 2) st=fail; note="$note: config unreadable" ;; esac; fi
  [ "$READING" = null ] && { st=fail; note="no reading"; }
  printf '{"exp":"dv2","pass":%s,"card":"%s","t0_ms":%s,"t1_ms":%s,"die_c_start":%s,"die_c_end":%s,"status":"%s","note":%s}\n' \
    "$PASS" "$CARD" "$T0" "$(now_ms)" "$READING" "$READING" "$st" "$(jstr "$note")" > "$OUT/block.json"
  log "dv2 Z1 p$PASS: $note"
  exit 0
fi

# =============================================================================================== sessions
# the pre-conditions that need no card (so a candidate that cannot start never takes the lock)
if [ "$KIND" = NAT ]; then
  why=$("${DV2PY[@]}" natok --data "$DV2_DATA" --now "$(now_ms)") || {
    echo "{\"t_ms\":$(now_ms),\"pass\":$PASS,\"why\":$(jstr "$why")}" >> "$DV2_DATA/nat-candidates.jsonl"; log "dv2 p$PASS: $why"; exit 0; }
fi
if [ "$KIND" = C1M ]; then
  why=$("${DV2PY[@]}" c1mok --data "$DV2_DATA" --now "$(now_ms)" --r0 99) || { skip_record "$why"; exit 0; }
fi
if [ "$KIND" = SMOKE ]; then
  SLOT=$("${DV2PY[@]}" slot --pass "$PASS"); now=$(now_ms)
  if [ "$SLOT" != 0 ] && [ "$now" -lt "$SLOT" ]; then
    [ $(( SLOT - now )) -gt 3600000 ] && { skip_record "the smoke's slot is more than 60 min ahead"; exit 0; }
    sleep $(( (SLOT - now) / 1000 ))
  fi
fi
if pgrep -u "$(id -u)" -f 'tools/claims-v3/queue\.sh' > /dev/null; then
  of=$(other_framework); [ -n "$of" ] && { log "dv2 p$PASS: another framework queue or block runs: $of"; exit 3; }
fi

# the gate BEFORE block_begin, whose first act after the lock is a 1 s die reading (review: no device access before
# et-who, who and the process scan)
if others_present || ours_running || [ -n "$(foreign_procs)" ] || [ -n "$(etwho_foreign)" ] || [ -n "$(other_framework)" ]; then
  log "dv2 p$PASS: another user, device process, holder or framework process present: not starting"; exit 3
fi
if ! dry; then n=$(modcount); [ -n "$n" ] && [ "$n" != 0 ] && { log "dv2 p$PASS: et_soc1 use count $n: not starting"; exit 3; }; fi
BEXP=dv2; [ -n "${DV2_VAL:-}" ] && BEXP=dv2v      # validation: the data go to build/claims-v3/<card>/dv2v/
block_begin "$BEXP" "$PASS"             # the card lock (fd 9) is held from here to the end
trap 'dv2_cleanup' EXIT
SESSION_T0=$(now_ms)
: > "$OUT/runs.jsonl"; : > "$OUT/launches.jsonl"; : > "$OUT/marks.jsonl"
"${DV2PY[@]}" binhash "heater=$HEATER" "heater_kernel=$HEATER_KERNEL" "ettelem_dv2=$ETTELEM" > "$OUT/binaries.json"
command -v et-lab-manifest > /dev/null && ! dry && timeout 30 et-lab-manifest > "$OUT/manifest.txt" 2>&1
mark session_begin "\"kind\":\"$KIND\",\"dry\":$(dry && echo true || echo false)"
dv2_on_abort() { session_json "${LAUNCHED_ANY:-false}" "aborted (exit $1): $2"; }
dv2_gate "session start"
dv2_level_pending_restore
LAUNCHED_ANY=false; SPLINES=; BLOCKS_DONE=0; LAST_HEAT_END=0
elapsed_s() { echo $(( ( $(now_ms) - SESSION_T0 ) / 1000 )); }
fits() {   # fits <worst-case seconds> <cap s>: the next step fits in the session cap and before the night's end
  [ $(( $(elapsed_s) + $1 )) -le "$2" ] || return 1
  [ "$END_BY" = 0 ] || [ $(( $(now_ms) + $1 * 1000 )) -le "$END_BY" ]
}

# ---- one run, recorded (T, ADD, RST, C1m, smoke). Sets RUN_EDGE_TIMEOUT when its edge never came.
record_run() {   # record_run <json of the run's own fields> ; merges the observables
  local obs=${OBS_JSON:-"{}"}
  python3 - "$OUT/runs.jsonl" "$1" "$obs" <<'PY'
import json, sys
r = json.loads(sys.argv[2]); o = json.loads(sys.argv[3] or "{}")
r["obs"] = o
for k in ("trip_s", "qualifies", "censored", "t_c_s", "censored_c"):
    if k in o:
        r[k] = o[k]
open(sys.argv[1], "a").write(json.dumps(r) + "\n")
PY
}
finish_run() {   # finish_run <idx> <target or -> : dump, dump check, post-run clock check, reset check, observables
  local idx=$1 tgt=${2:--} kend
  dv2_run_end_quiet
  dv2_sptrace "$OUT/sp-$idx.bin"
  dv2_dumpcheck "$OUT/sp-$idx.bin" || dv2_abort 1 "a governor error line in sp-$idx.bin: the night stops"
  OBS_JSON='{}'; POST_RC=; POST_WHY=; RESET_WHY=
  if [ -n "${LAST_LAUNCH_END:-}" ]; then
    # the kernel end of the measured launch (its SPARSITY lines); a run with lifts only: the last lift's process end
    if [ -n "${MEASURED:-}" ]; then kend=$("${DV2PY[@]}" kend --heater "$OUT/heater-$idx.out" --fallback "$LAST_LAUNCH_END")
    else kend=$LAST_LAUNCH_END; fi
    dv2_postcheck "$RUN_TEL" "$kend"
    LAST_HEAT_END=$kend
  fi
  if [ -n "${MEASURED:-}" ]; then
    RESET_WHY=$("${DV2PY[@]}" resets --tel "$RUN_TEL" --t0 "$MEAS_T0" 2>/dev/null) || true
    OBS_JSON=$("${DV2PY[@]}" runobs --tel "$RUN_TEL" --heater "$OUT/heater-$idx.out" --K "${K_RUN:-66}" \
               ${tgt:+$( [ "$tgt" != - ] && echo "--target $tgt")} --stop-ms "${ST_PLANSTOP:--}" 2>/dev/null) || OBS_JSON='{}'
  fi
  gzip -f "$RUN_TEL" 2>/dev/null; for f in "$OUT/heater-$idx.out" "$OUT/heater-$idx-pre.out"; do [ -f "$f" ] && gzip -f "$f"; done
}

# ---- the smoke (row 4; also the first step of a NAT session)
dv2_smoke() {
  local R
  R=$(die_c)
  mark smoke_reading "\"die_c\":$(jnum "$R")"
  dv2_sptrace "$OUT/sp-smoke0.bin"
  dv2_dumpcheck "$OUT/sp-smoke0.bin" || dv2_abort 1 "a governor error line in the first dump: the night stops"
  dv2_z2 "$OUT/z2-smoke"
  dv2_config "$OUT/config-smoke.json"
  local trc=0; dv2_threshold_ok "$OUT/config-smoke.json" || trc=$?
  [ "$trc" = 0 ] || dv2_abort 1 "the threshold does not read 65 (or config unreadable, rc $trc)"
  dv2_state_table smoke-start "$OUT/config-smoke.json"
  RUN_STOP=; MEASURED=; LAST_LAUNCH_END=; LIFT_LAST_END=
  dv2_gate "before the smoke"
  dv2_run_begin smoke once
  dv2_sleep 1; dv2_live || true
  echo "resetnow" >> "$RUN_CTL"
  local rs=ok; dv2_wait_reset "$P_reset_confirm_s" || rs=missing
  echo "stop700 $(awk -v s="$P_stop_after_700_s" 'BEGIN{printf "%d", s*1000}') $(now_ms)" >> "$RUN_CTL"
  dv2_gate "before the smoke launch"
  dv2_launch smoke single 0xffffffff 4 "$P_smoke_launch_s" "$RUN_SF"
  LAUNCHED_ANY=true; MEASURED=1; MEAS_T0=$L_TS; LAST_LAUNCH_END=$L_TE
  dv2_tail "$P_tail_s"
  dv2_state || true
  finish_run smoke
  local kinds
  kinds=$(python3 "$DV2_DIR/sptrace_events.py" events "$OUT/sp-smoke.bin" 2>/dev/null | python3 -c '
import json, sys, collections
c = collections.Counter(json.loads(l)["kind"] for l in sys.stdin if l.strip())
print(json.dumps(dict(c)))' 2>/dev/null || echo '{}')
  mark smoke "\"reset\":\"$rs\",\"reset_check\":$(jstr "$RESET_WHY"),\"post\":$(jstr "$POST_WHY"),\"sp_kinds\":$kinds,\"rc\":$LAST_RC"
  record_run "{\"idx\":\"smoke\",\"kind\":\"SMOKE\",\"name\":\"UNI32@4\",\"rc\":$LAST_RC,\"reset\":\"$rs\",\"reset_check\":$(jstr "$RESET_WHY"),\"post_rc\":${POST_RC:-null},\"post\":$(jstr "$POST_WHY")}"
  [ "$LAST_RC" = 0 ] || dv2_abort 1 "smoke: heater rc $LAST_RC"
  [ "$rs" = ok ] || dv2_abort 1 "smoke: the one-shot reset did not show in the sampler (ettelem-dv2 --reset-once-file)"
  log "dv2 smoke: rest $R C; reset $rs; $RESET_WHY; post $POST_WHY; SP lines $kinds"
}

# ---- a T-run (T, ADD, RST): lifts, the falling S+1 -> S edge with the one-shot reset, one launch with the stop 2 s
# after the first 700 sample, a 10 s tail, the dump, the checks
EDGE_TIMEOUTS=0
dv2_trun() {   # dv2_trun <idx> <kind T|ADD|RST> <name> <S> <block> <slot>
  local idx=$1 kind=$2 name=$3 S=$4 blk=$5 slot=$6 mask per mins mode=once
  read -r mask per mins <<< "$("${DV2PY[@]}" rundef "$name")"
  [ "$kind" = RST ] && mode=periodic
  dv2_gate "before run $idx"
  RUN_STOP=; LIFTS=0; LIFT_WHY=; EDGE_OK=; EDGE_T=; EDGE_TAUC=; EDGE_S1=; EDGE_WAIT_S=; MEASURED=; MEAS_T0=
  LAST_LAUNCH_END=; LIFT_LAST_END=; RUN_EDGE_TIMEOUT=; local rs=- rc=null since_heat=null
  [ "$LAST_HEAT_END" != 0 ] && since_heat=$(( ( $(now_ms) - LAST_HEAT_END ) / 1000 ))
  dv2_run_begin "$idx" "$mode"
  mark run_begin "\"idx\":$idx,\"kind\":\"$kind\",\"name\":\"$name\",\"S\":$S,\"block\":$blk,\"slot\":$slot"
  dv2_live || true
  if [ -z "${RUN_STOP:-}" ] && [ "$ST_MEAN" -lt $(( S + 1 )) ]; then
    dv2_lift $(( S + 1 )) "$P_lift_mask" "$P_lift_per" "$P_lift_s" "$P_lift_max" || true
    [ "$LIFTS" -gt 0 ] && { LIFT_LAST_END=$L_TE; LAST_LAUNCH_END=$L_TE; LAUNCHED_ANY=true; }
  fi
  if [ -z "${RUN_STOP:-}" ] && { [ "$LIFT_WHY" != max ] || [ "$ST_MEAN" -ge $(( S + 1 )) ]; }; then
    dv2_edge_wait "$S" "$P_edge_cap_s" || true
  fi
  if [ -n "$EDGE_OK" ] && [ -z "${RUN_STOP:-}" ]; then
    EDGE_TIMEOUTS=0
    if [ "$mode" = once ]; then rs=ok; dv2_wait_reset "$P_reset_confirm_s" || rs=missing; fi
    if [ "$rs" != missing ]; then
      echo "stop700 $(awk -v s="$P_stop_after_700_s" 'BEGIN{printf "%d", s*1000}') $(now_ms)" >> "$RUN_CTL"
      dv2_gate "before the launch of run $idx"
      dv2_launch "$idx" single "$mask" "$per" "$P_launch_s" "$RUN_SF"
      rc=$LAST_RC; LAUNCHED_ANY=true; MEASURED=1; MEAS_T0=$L_TS; LAST_LAUNCH_END=$L_TE
      dv2_tail "$P_tail_s"
    fi
  elif [ -z "${RUN_STOP:-}" ]; then
    RUN_EDGE_TIMEOUT=1; EDGE_TIMEOUTS=$(( EDGE_TIMEOUTS + 1 ))
    mark edge_timeout "\"idx\":$idx,\"consecutive\":$EDGE_TIMEOUTS,\"lift_why\":\"$LIFT_WHY\""
  fi
  dv2_state || true
  finish_run "$idx"
  record_run "$(python3 -c '
import json, sys
def val(b):
    try:
        return json.loads(b)
    except Exception:
        return b
print(json.dumps({a: val(b) for a, b in zip(sys.argv[1::2], sys.argv[2::2])}))' \
    idx "$idx" kind "$kind" name "$name" mask "\"$mask\"" per_shire "$per" minions "$mins" S "$S" K "$K_RUN" block "$blk" slot "$slot" \
    cand "${DEV1_CAND:-0}" N "${DEV1_N:-128}" KS "${DEV1_KS:-4}" launch_s "$P_launch_s" stop_after_700_s "$P_stop_after_700_s" \
    lifts "$LIFTS" lift_why "\"${LIFT_WHY:-}\"" edge_ok "$([ -n "$EDGE_OK" ] && echo true || echo false)" \
    edge_ms "$(jnum "$EDGE_T")" s1_ms "$(jnum "$EDGE_S1")" tau_c_s "$(jnum "$EDGE_TAUC")" edge_wait_s "$(jnum "$EDGE_WAIT_S")" \
    edge_timeout "$([ -n "$RUN_EDGE_TIMEOUT" ] && echo true || echo false)" since_heat_s "$since_heat" \
    reset "\"$rs\"" reset_check "$(jstr "$RESET_WHY")" rc "$rc" stop "$(jstr "${RUN_STOP:-}")" \
    planstop_ms "$(jnum "${ST_PLANSTOP:-}")" t700_live_ms "$(jnum "${ST_T700:-}")" post_rc "$(jnum "$POST_RC")" post "$(jstr "$POST_WHY")" \
    sp_lines "$([ -n "$SPLINES" ] && echo true || echo false)")"
  log "dv2 run $idx ($kind $name, S $S): lifts $LIFTS, edge ${EDGE_OK:+ok}${RUN_EDGE_TIMEOUT:+TIMEOUT}, rc $rc, reset $rs, stop ${RUN_STOP:-none}, post ${POST_WHY:-none}"
}

# =============================================================================================== the smoke
if [ "$KIND" = SMOKE ]; then
  R0=$(die_c); K_RUN=66
  dv2_smoke
  dv2_config "$OUT/config-end.json"; dv2_state_table end "$OUT/config-end.json"
  session_json true "smoke ok"
  dv2_gzip_all; trap - EXIT
  block_end ok "smoke: R0 $R0 C; $RESET_WHY; post $POST_WHY"
  exit 0
fi

# =============================================================================================== C1m (LOOP only)
if [ "$KIND" = C1M ]; then
  R0=$(die_c); K_RUN=66
  why=$("${DV2PY[@]}" c1mok --data "$DV2_DATA" --now "$(now_ms)" --r0 "$R0") || {
    session_json false "not run: $why"; trap - EXIT; block_end ok "skipped: $why"; exit 0; }
  E=$(( R0 + P_c1m_edge_over )); TGT=$(( E + P_c1m_rise ))
  C1M_END=$("${DV2PY[@]}" nightkey c1m_end_by)          # C1m ends by then (night.json), besides its 65 min cap
  if [ "$C1M_END" != 0 ] && { [ "$END_BY" = 0 ] || [ "$C1M_END" -lt "$END_BY" ]; }; then END_BY=$C1M_END; fi
  if [ "$TGT" -ge $(( P_cap_mean_c - 2 )) ]; then session_json false "R0 $R0: target $TGT too close to the cap"; trap - EXIT; block_end ok "skipped: R0 $R0 too warm"; exit 0; fi
  BRANCH=LOOP
  mark c1m_begin "\"r0\":$R0,\"E\":$E,\"target\":$TGT"
  log "dv2 C1m: R0 $R0 C, edge $((E + 1)) -> $E, target $TGT"
  RUN_WORST=$(( P_c1m_preheat_max * (P_c1m_preheat_s + 1) + P_edge_cap_s + P_c1m_max_launches * (P_c1m_launch_s + 2) + P_tail_s + 30 ))
  n=0; COOL_SEEN=
  while read -r _ blk slot name; do
    fits "$RUN_WORST" "$P_c1m_cap_s" || { mark cap "\"why\":\"65 min C1m cap or the night's end before run $((n + 1))\""; break; }
    n=$(( n + 1 )); idx=c$n
    read -r mask per mins <<< "$("${DV2PY[@]}" rundef "$name")"
    dv2_gate "before C1m run $n"
    RUN_STOP=; LIFTS=0; LIFT_WHY=; EDGE_OK=; EDGE_T=; EDGE_TAUC=; EDGE_S1=; EDGE_WAIT_S=; MEASURED=; MEAS_T0=; LAST_LAUNCH_END=; LIFT_LAST_END=
    rs=-; nl=0; rcs=
    dv2_run_begin "$idx" once
    mark run_begin "\"idx\":\"$idx\",\"kind\":\"C1M\",\"name\":\"$name\",\"block\":$blk,\"slot\":$slot"
    dv2_live || true
    if [ "$ST_MEAN" -le "$P_thr" ] || [ "$ST_MHZ" != 600 ]; then   # out of the thermal loop: the governor is free again
      COOL_SEEN=$ST_MEAN; mark c1m_out_of_loop "\"mean\":$ST_MEAN,\"mhz\":\"$ST_MHZ\""; dv2_run_end_quiet; break
    fi
    if [ "$ST_MEAN" -lt $(( E + 2 )) ]; then
      LIFT_REQUIRE_600=1 dv2_lift $(( E + 2 )) "$P_c1m_preheat_mask" "$P_c1m_preheat_per" "$P_c1m_preheat_s" "$P_c1m_preheat_max" || true
      [ "$LIFTS" -gt 0 ] && { LIFT_LAST_END=$L_TE; LAST_LAUNCH_END=$L_TE; LAUNCHED_ANY=true; }
    fi
    [ -z "${RUN_STOP:-}" ] && dv2_edge_wait "$E" "$P_edge_cap_s" || true
    if [ -n "$EDGE_OK" ] && [ -z "${RUN_STOP:-}" ]; then
      EDGE_TIMEOUTS=0
      rs=ok; dv2_wait_reset "$P_reset_confirm_s" || rs=missing
      if [ "$rs" = ok ]; then
        echo "target $TGT $(now_ms)" >> "$RUN_CTL"
        MEASURED=1
        while [ "$nl" -lt "$P_c1m_max_launches" ]; do
          dv2_live || break
          [ -e "$RUN_SF" ] && break
          [ "$ST_MHZ" = 600 ] || { mark c1m_offclock "\"mhz\":\"$ST_MHZ\""; break; }
          dv2_gate "between C1m launches"
          dv2_launch "$idx" chain "$mask" "$per" "$P_c1m_launch_s" "$RUN_SF"
          [ "$nl" = 0 ] && MEAS_T0=$L_TS
          nl=$(( nl + 1 )); rcs="${rcs:+$rcs,}$LAST_RC"; LAUNCHED_ANY=true; LAST_LAUNCH_END=$L_TE
          [ "$LAST_RC" = 0 ] || break
          dv2_sleep "$P_gap_between_launches_s"
        done
        dv2_tail "$P_tail_s"
      fi
    else
      EDGE_TIMEOUTS=$(( EDGE_TIMEOUTS + 1 )); mark edge_timeout "\"idx\":\"$idx\",\"consecutive\":$EDGE_TIMEOUTS"
    fi
    dv2_state || true
    finish_run "$idx" "$TGT"
    record_run "{\"idx\":\"$idx\",\"kind\":\"C1M\",\"name\":\"$name\",\"mask\":\"$mask\",\"per_shire\":$per,\"minions\":$mins,\"block\":$blk,\"slot\":$slot,\"r0\":$R0,\"E\":$E,\"target\":$TGT,\"preheat_bursts\":$LIFTS,\"edge_ok\":$([ -n "$EDGE_OK" ] && echo true || echo false),\"edge_ms\":$(jnum "$EDGE_T"),\"tau_c_s\":$(jnum "$EDGE_TAUC"),\"edge_wait_s\":$(jnum "$EDGE_WAIT_S"),\"reset\":\"$rs\",\"reset_check\":$(jstr "$RESET_WHY"),\"launches\":$nl,\"rcs\":[$rcs],\"stop\":$(jstr "${RUN_STOP:-}"),\"target_ms\":$(jnum "${ST_TARGET:-}"),\"post_rc\":$(jnum "$POST_RC"),\"post\":$(jstr "$POST_WHY")}"
    log "dv2 C1m run $n ($name, block $blk): edge ${EDGE_OK:+ok}, launches $nl, target ${ST_TARGET:--}, stop ${RUN_STOP:-none}"
    [ "$EDGE_TIMEOUTS" -ge "$P_edge_timeouts_end" ] && { mark session_end "\"why\":\"two consecutive edge time-outs\""; break; }
    # the card left its thermal loop (a preheat or launch saw a clock off 600 MHz), or a safety cap stopped the run:
    # C1m ends (the run is void)
    if [ "$LIFT_WHY" = offclock ] || [ -n "${RUN_STOP:-}" ] || python3 -c 'import json,sys; sys.exit(0 if (json.loads(sys.argv[1] or "{}").get("off600") or 0) > 0 else 1)' "$OBS_JSON"; then
      COOL_SEEN=${ST_MEAN:-?}; mark c1m_out_of_loop "\"after\":\"$idx\",\"lift_why\":\"$LIFT_WHY\""; break
    fi
    [ "$slot" = 3 ] && BLOCKS_DONE=$blk
  done < <("${DV2PY[@]}" plan-c1m)
  dv2_z2 "$OUT/z2-end"; dv2_config "$OUT/config-end.json"
  dv2_threshold_ok "$OUT/config-end.json" || true
  dv2_state_table end "$OUT/config-end.json"
  session_json "$LAUNCHED_ANY" "C1m: $n runs, $BLOCKS_DONE complete blocks${COOL_SEEN:+; stopped out of the thermal loop at a reading of $COOL_SEEN}"
  dv2_gzip_all; trap - EXIT
  block_end ok "C1m at R0 $R0 C: $n runs, $BLOCKS_DONE complete blocks${COOL_SEEN:+, ended out of the loop at $COOL_SEEN C}"
  exit 0
fi

# =============================================================================================== a NAT session
R0=$(die_c); K_RUN=66
read -r BRANCH S_BR _ <<< "$("${DV2PY[@]}" branch --r0 "$R0")"
mark branch "\"r0\":$(jnum "$R0"),\"branch\":\"$BRANCH\",\"S\":$(jnum "$S_BR")"
case "$BRANCH" in NAT-*) ;; *) session_json false "R0 $R0 C: $BRANCH, no NAT session"; trap - EXIT; block_end ok "skipped: R0 $R0 C is $BRANCH"; exit 0 ;; esac
log "dv2 NAT: R0 $R0 C -> $BRANCH (S $S_BR)"
dv2_probe "$OUT/probe"
case "$PROBE_CLASS" in
  ALIVE|ALIVE_CANDIDATE) ;;
  *) dv2_alert PROBE-SILENT "the R0 probe says ${PROBE_CLASS:-nothing} at R0 $R0 C (<= 64): evidence of a latch; no heat" nostop
     session_json true "probe $PROBE_CLASS at R0 $R0: no heat, alert"; dv2_gzip_all; trap - EXIT
     block_end ok "probe $PROBE_CLASS at R0 $R0 C: ALERT-PROBE-SILENT, no heat"; exit 0 ;;
esac
dv2_smoke
SPLINES=1
dv2_level_begin sp-before                     # O2: WARNING after ALIVE (clears SPLINES when nothing is set)
mark sp_lines "\"registered\":$([ -n "$SPLINES" ] && echo true || echo false),\"level_found\":\"${LEVEL_FOUND:-}\""
devlog DEV-5-input "\"sp_lines\":$([ -n "$SPLINES" ] && echo true || echo false),\"level_found\":\"${LEVEL_FOUND:-}\",\"probe\":\"$PROBE_CLASS\""
T_WORST=$(( P_lift_max * (P_lift_s + 3) + P_edge_cap_s + 8 + P_tail_s + 30 ))
BLOCK_WORST=$(( 4 * T_WORST ))
DEV1_CAND=0; DEV1_N=128; DEV1_KS=4
REST_S=$P_block_rest_s
idx=0
if fits $(( 2 * T_WORST )) "$P_nat_cap_s"; then
  idx=$(( idx + 1 )); dv2_trun "$idx" ADD ADD1 "$S_BR" 0 0
fi
b=0
while :; do
  [ "$EDGE_TIMEOUTS" -ge "$P_edge_timeouts_end" ] && { mark session_end "\"why\":\"two consecutive edge time-outs\""; break; }
  fits $(( BLOCK_WORST + T_WORST )) "$P_nat_cap_s" || { mark cap "\"why\":\"a block's worst case plus the closing ADD does not fit (60 min, 08:00)\""; break; }
  b=$(( b + 1 ))
  if [ "$BRANCH" != NAT-1 ] && [ "$b" -le 3 ]; then
    eval "$("${DV2PY[@]}" dev1 --data "$OUT")"
    devlog DEV-1 "\"block\":$b,\"state\":$DEV1_JSON"
  fi
  S=$S_BR
  if [ "$BRANCH" = NAT-4 ] || [ "$BRANCH" = NAT-3 ]; then S=$(( 66 - DEV1_KS )); [ "$S" -lt "$S_BR" ] && S=$S_BR; fi
  mark block_begin "\"block\":$b,\"S\":$S,\"N\":$DEV1_N,\"KS\":$DEV1_KS"
  slot=0; BLOCK_TIMEOUTS=0
  while read -r _ s name; do
    idx=$(( idx + 1 )); slot=$s
    dv2_trun "$idx" T "$name" "$S" "$b" "$s"
    [ -n "$RUN_EDGE_TIMEOUT" ] && BLOCK_TIMEOUTS=$(( BLOCK_TIMEOUTS + 1 ))
    [ "$EDGE_TIMEOUTS" -ge "$P_edge_timeouts_end" ] && break
  done < <("${DV2PY[@]}" plan-t --block "$b" --branch "$BRANCH" --n "$DEV1_N")
  BLOCKS_DONE=$b
  mark block_end "\"block\":$b,\"edge_timeouts\":$BLOCK_TIMEOUTS"
  # DEV-2 (launch length), DEV-3 (stop delay) after block 1; DEV-10 (rest) after every block. Validation: fixed.
  if [ "$b" = 1 ] && [ -z "${DV2_VAL:-}" ]; then
    read -r D2 D3 <<< "$(python3 - "$OUT" <<'PY'
import json, sys, os
sys.path.insert(0, "tools/claims-v3/dv2")
from dv2lib import load_jsonl
out = sys.argv[1]
L = [l for l in load_jsonl(os.path.join(out, "launches.jsonl")) if l.get("seconds") == 7]
d2 = "8" if L and all(l.get("wall_s", 99) <= 8.0 for l in L) else "7"
R = [r for r in load_jsonl(os.path.join(out, "runs.jsonl")) if r.get("kind") == "T" and r.get("trip_s") is not None]
seen = [r for r in R if (r.get("obs") or {}).get("saw600_before_stop")]
d3 = "2.0" if not R or len(seen) >= 0.8 * len(R) else "3.0"
print(d2, d3)
PY
)"
    devlog DEV-2 "\"launch_s\":$D2,\"rule\":\"8 s only if every 7 s process took <= 8.0 s wall\""
    devlog DEV-3 "\"stop_after_700_s\":$D3,\"rule\":\"3.0 s if < 80% of tripped runs show 600 MHz before the stop\""
    P_launch_s=$D2; P_stop_after_700_s=$D3
  fi
  if [ "$BLOCK_TIMEOUTS" -ge 2 ] && [ "$REST_S" -lt 600 ]; then REST_S=600; devlog DEV-10 "\"rest_s\":600,\"block\":$b,\"edge_timeouts\":$BLOCK_TIMEOUTS"; fi
  [ "$EDGE_TIMEOUTS" -ge "$P_edge_timeouts_end" ] && continue
  fits $(( REST_S + BLOCK_WORST + T_WORST )) "$P_nat_cap_s" || { mark cap "\"why\":\"no further block fits after the rest\""; break; }
  mark rest "\"s\":$REST_S"
  rest_end=$(( $(now_ms) + REST_S * 1000 ))
  while [ "$(now_ms)" -lt "$rest_end" ]; do dv2_sleep 30; dv2_gate "rest"; done
done
# DEV-12: two periodic-reset runs, if >= 10 min remain
if [ -z "${DV2_VAL:-}" ] && [ "$EDGE_TIMEOUTS" -lt "$P_edge_timeouts_end" ] && fits $(( 3 * T_WORST )) "$P_nat_cap_s"; then
  for k in 1 2; do idx=$(( idx + 1 )); dv2_trun "$idx" RST UNI32@4 "$S_BR" 0 "$k"; done
fi
if fits "$T_WORST" "$P_nat_cap_s"; then idx=$(( idx + 1 )); dv2_trun "$idx" ADD ADD1 "$S_BR" 0 9; fi
LEVEL_CHECK=
dv2_level_restore
dv2_z2 "$OUT/z2-end"; dv2_config "$OUT/config-end.json"
dv2_threshold_ok "$OUT/config-end.json" || true
dv2_state_table end "$OUT/config-end.json"
session_json true "NAT $BRANCH at R0 $R0: $BLOCKS_DONE T-blocks, $idx runs"
dv2_gzip_all; trap - EXIT
block_end ok "NAT $BRANCH at R0 $R0 C: $BLOCKS_DONE T-blocks, $idx runs, probe $PROBE_CLASS${LEVEL_CHECK:+; $LEVEL_CHECK}"
exit 0
