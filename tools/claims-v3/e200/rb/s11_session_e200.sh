#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum), the box step "the sitting" (this file is s11), ONE SITTING A CALL:
# E200's sitting on aifoundry2 card 0, launched detached on the box (it returns at once), right after step 7's reads (the sitting's first
# card command, stamped by step 7's wrapper). E197's step 9 (tools/claims-v3/e197/rb/s11_a3_session_e197.sh, unchanged beside it) on this
# box, with E194's launch lines (tools/claims-v3/e194/rb/s11_session_e194_v2.sh, unchanged beside it):
#   - at the desk: the window rule (written today for E200 and this sitting); THE QUIET DESK FLAG raised; today's build (RB_OUT/e200-built.txt)
#     and today's dry pass for this sitting (RB_OUT/e200-<n>-dry-ok.txt); THE FIRST CARD COMMAND from RB_OUT/e200-<n>-first.txt (step 7's
#     wrapper: FIRST, the PLAN decided there, the firmware identity FWGATE and step 7's folder FIRSTDIR), written today, at most 120 s ago
#     (E200_FIRST_MAX_S; else 16: its cap counts from it), and the plan's cap from it before the window's last end (else 16);
#   - on the box: k6's guard's first lines, verbatim (no runbook job running, no card session of ours: rb_guard_text's), then THE LAB'S
#     FIRMWARE GATE in place of k6's identity by continuity (which refuses every boot after E69's read: aifoundry2 booted 2026-11-13
#     16:53:28 PST): `fwgate.py guard --box aifoundry2 --card 0 --extra <step 7's folder>` from E200's root must print "identity: ... ok"
#     (E200.md 8), else IDENTITY-STOP: 16, nothing launched; THE REST RULE again (rb/rest_rule_e200.sh; it held at the first card command,
#     step 7); today's dry pass for this sitting (a2-dry-e200-<n> ended rc 0 today), today's build (REGFILE-BUILT in a2-build-e200's output
#     today and E200's root's build/regfile-built.txt written today); NO SECOND TRY OF A SITTING ON THE DAY ITS SMOKE FAILED (a real E200 log
#     of this sitting today reading "the runner's smoke gate: failed" or "the kit's smoke check: FAILED": E197's kit's reading of E197.md 11,
#     E200.md 13); NO SITTING ON A DAY AN E200 SITTING'S DIE GATE HELD IT OFF (a real E200 log of today reading "GATE-STOP: the die gate:":
#     E200.md 9's "else no sitting that day"; fix-e200, verify-e200's F3; step 7 reads it first);
#     for sitting 2, SITTING 1 HELD FIRST (a real sitting-1 log whose SITTING-RESULT reads smoke passed, at least one train block
#     complete, no card stop: E197.md 6) AND NO CRASHED SITTING 1; THE P2 COUNT right before the launch (device-named processes and session or
#     queue scripts of ours on this box must read 0; read again up to 5 times 2 s apart, else REFUSED: no launch);
#   - then session_e200.sh detached, DRY unset, ET_DEVICES and V3_DEVICE unset, with E200_T0, E200_SIT, E200_PLAN, E200_FIRST, the window's
#     last end, harness-e200.json's sha256 from the lab clone, E200_FIRSTDIR and E200_FWGATE; the T0 written on the box
#     (build/q141k/e200-<n>.T0) and in RB_OUT (e200-<n>-T0.txt), which steps 10 and 11 read.
#   RB_QUIET=<the flag file> bash tools/claims-v3/e200/rb/s11_session_e200.sh 1|2
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e200.sh"
rb_init s11_session
sit=${1:-}
e200_sit_ok "$sit" || rb_die $RB_E_USAGE "usage: s11_session_e200.sh 1|2 (the sitting this RB_OUT's window names)"
e200_window "$sit"
e200_quiet
[ -n "${RB_DRY:-}" ] || e200_built_today || rb_die $RB_E_USAGE "regfile was not built today (RB_OUT/e200-built.txt, step 6's wait): run step 6 first"
[ -n "${RB_DRY:-}" ] || [ -f "$RB_OUT/e200-$sit-dry-ok.txt" ] || rb_die $RB_E_USAGE "no dry pass ended rc 0 today for sitting $sit in this RB_OUT: run step 8 first"
if [ -n "${RB_DRY:-}" ]; then
  echo "--- gate: <RB_OUT>/e200-$sit-first.txt (step 7's wrapper) written today: FIRST at most $E200_FIRST_MAX_S s ago, the PLAN's cap from FIRST before the last end, FWGATE and FIRSTDIR"
  first=1794800000; plan=full; [ "$sit" = 2 ] && plan=ext; cap=$(e200_cap_s "$plan"); fw=read; fd=build/e200/first-s$sit-$first
else
  E200_SIT=$sit
  e200_first || rb_die $RB_E_USAGE "RB_OUT holds no readable e200-$sit-first.txt: run step 7 (s09_reads_e200.sh $sit) first"
  first=$E200_FIRST; plan=$E200_PLAN_CHOSEN; cap=$(e200_cap_s "$plan")
  fw=$(sed -nE 's/^FWGATE=(continuity|read)$/\1/p' "$RB_OUT/e200-$sit-first.txt" | head -n 1)
  fd=$(sed -nE 's/^FIRSTDIR=(build\/e200\/first-s[12]-[0-9]+)$/\1/p' "$RB_OUT/e200-$sit-first.txt" | head -n 1)
  case "$sit:$plan" in 1:full|1:short|2:ext) ;; *) rb_die $RB_E_USAGE "sitting $sit with plan $plan: refused" ;; esac
  [ "$(TZ=America/Los_Angeles e200_fmt "$first" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_GATE "the first card command was not today: no sitting"
  now=$(date +%s)
  [ $((now - first)) -le "$E200_FIRST_MAX_S" ] || rb_die $RB_E_GATE "the first card command (step 7) was $((now - first)) s ago, more than $E200_FIRST_MAX_S s: its cap counts from it; no sitting $sit on this RB_OUT today (a new try needs its own RB_OUT and step 7)"
  [ $((first + cap)) -le "$RB_LAST_END_EPOCH" ] || rb_die $RB_E_GATE "the plan's cap ($cap s from the first card command) passes the window's last end: no sitting"
  [ -n "$fw" ] && [ "$fd" = "build/e200/first-s$sit-$first" ] || rb_die $RB_E_USAGE "e200-$sit-first.txt does not read FWGATE= and FIRSTDIR= for this sitting: run step 7 first"
fi
hs=$(e200_harness_sha); [ -n "${RB_DRY:-}" ] && hs=${hs:-HARNESS-SHA256}
[ -n "$hs" ] || rb_die $RB_E_USAGE "harness-e200.json's sha256 could not be read in the lab clone"
f=$(rb_file e200)
{ rb_prelude aifoundry2
  echo "SIT=$sit; PLAN=$plan; FIRST=$first; ROOT=$E200_ROOT; HSHA=$hs; FD=$fd; FW=$fw; LAST_END_EPOCH=${RB_LAST_END_EPOCH:-0}; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text | sed -n '1,3p'
  cat <<'EOF2'
[ -d "$FD" ] || { echo "REFUSED: step 7's folder $FD is not on the box: run step 7 first"; exit 3; }
fg=$(python3 -I -B "$ROOT/tools/claims-v3/fwgate/fwgate.py" guard --box aifoundry2 --card 0 --extra "$FD" 2>&1); fgr=$?
printf '%s\n' "$fg" | grep -E '^(identity|IDENTITY-STOP|note): ' | cut -c1-300
if [ "$fgr" -ne 0 ] || ! printf '%s\n' "$fg" | grep -qE '^identity: aifoundry2 card 0 .*: ok$'; then
  printf '%s\n' "$fg" | grep -q '^IDENTITY-STOP' || echo "IDENTITY-STOP: fwgate's guard exited $fgr without its identity line: nothing launched"
  exit 3
fi
EOF2
  cat "$RB_E200_DIR/rest_rule_e200.sh"
  cat <<'EOF2'
job_ok_today "a2-dry-e200-$SIT" || { echo "REFUSED: E200 sitting $SIT's dry pass (step 8's job a2-dry-e200-$SIT) has not ended rc 0 today"; exit 3; }
echo "dry pass: a2-dry-e200-$SIT ended rc 0 today"
fresh build/q141k/jobs/a2-build-e200.out && grep -q '^REGFILE-BUILT rc=0' build/q141k/jobs/a2-build-e200.out ||
  { echo "REFUSED: regfile was not built today (step 6's job a2-build-e200)"; exit 3; }
fresh "$ROOT/build/regfile-built.txt" || { echo "REFUSED: E200's root holds no build record written today"; exit 3; }
echo "build: REGFILE-BUILT today"
today=$(date +%F)
for L in build/e200/T[0-9]*/session.log; do
  [ -f "$L" ] || continue
  case "$L" in *-dry*) continue ;; esac
  if grep -qE "^$today [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ GATE-STOP: the die gate:" "$L"; then
    echo "REFUSED: an E200 sitting's die gate held it off today (${L%/session.log}): no sitting that day (E200.md 9)"; exit 3
  fi
  grep -q "E200 sitting $SIT," "$L" || continue
  if grep -qE "^$today [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ (the runner's smoke gate: failed|the kit's smoke check: FAILED)" "$L"; then
    echo "REFUSED: E200 sitting $SIT's smoke failed today (${L%/session.log}): no second try that day (E200.md 13)"; exit 3
  fi
done
if [ "$SIT" = 2 ]; then
  a=""; cr=""; why=""
  for L in build/e200/T[0-9]*/session.log; do
    [ -f "$L" ] || continue
    case "$L" in *-dry*) continue ;; esac
    grep -q 'E200 sitting 1,' "$L" && grep -q 'session end' "$L" || continue
    if grep -q 'the trains ended without a registered stop' "$L"; then cr=$L; continue; fi
    r=$(grep -m1 'SITTING-RESULT: ' "$L" | sed 's/.*SITTING-RESULT: //')
    case "$r" in "smoke passed; train blocks complete "[1-9]*"card stop none") a=$L ;; *) why="$why ${L%/session.log}: ${r:-no SITTING-RESULT}" ;; esac
  done
  [ -z "$cr" ] || { echo "REFUSED: E200 sitting 1 ended without a registered stop (a crash: ${cr%/session.log}): no sitting 2 before a dated note decides"; exit 3; }
  [ -n "$a" ] || { echo "REFUSED: no E200 sitting 1 on this box that ran its smoke and at least one train block with no stop naming the card (E197.md 6, E200.md 5:${why:- none found}): sitting 2 needs a dated amendment"; exit 3; }
  echo "sitting 1 held first: ${a%/session.log}"
fi
i=0
while :; do
  i=$((i + 1)); P2=$(p2_count); echo "quiet desk: $P2 (read $i)"
  case "$P2" in "P2 0 "*) break ;; esac
  [ "$i" -ge 5 ] && { echo "REFUSED: the P2 count is not 0 after $i reads (a device-named process or a session or queue script of ours on aifoundry2): no launch"; exit 3; }
  sleep 2
done
mkdir -p build/e200 build/q141k
T0=$(date +%s)
echo "$T0" > "build/q141k/e200-$SIT.T0"
unset ET_DEVICES V3_DEVICE
env -u DRY E200_T0="$T0" E200_SIT="$SIT" E200_PLAN="$PLAN" E200_FIRST="$FIRST" E200_LAST_END_EPOCH="$LAST_END_EPOCH" E200_HARNESS_SHA256="$HSHA" \
  E200_FIRSTDIR="$FD" E200_FWGATE="$FW" setsid nohup bash "$ROOT/tools/claims-v3/e200/session_e200.sh" > "build/q141k/e200-$SIT-T$T0.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e200-$SIT T0 $T0 $(date '+%F %T %Z') (sitting $SIT, plan $PLAN; first card command $FIRST; the firmware $FW; last start $LAST_START, last end $LAST_END)"
tail -n 6 "build/e200/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry2
rb_remote launch aifoundry2 "launch E200 sitting $sit, detached, past fwgate's guard" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^IDENTITY-STOP' && rb_die $RB_E_GATE "$(grep -m1 '^IDENTITY-STOP' "$RB_CAP" | cut -c1-300) (the lab's firmware gate, E200.md 8; nothing launched; report to the owner)"
rb_launched "e200-$sit"
rb_has '^identity: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^identity: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^quiet desk: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep '^quiet desk: ' "$RB_CAP" | tail -n 1)" >> "$RB_LOG"
t0=$(rb_val "^LAUNCHED e200-$sit T0 ([0-9]+) .*\$")
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e200-$sit-T0.txt"
rb_say "E200 sitting $sit launched on aifoundry2 card 0 (T0 $t0, plan $plan) past fwgate's guard; wait with s20_wait_e200.sh $sit (bounded)"
