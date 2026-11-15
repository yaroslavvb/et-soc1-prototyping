#!/usr/bin/env bash
# E191's kit, dated note 2 (Q184, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after
# E191's first session stopped at its smoke gate by a kit defect (1a4bc1e3), before any E191 pass datum; KIT.md.dated-note-2.md):
# step 9 v2: rb/s11_a1_session_e191.sh (unchanged beside it) launching SESSION V2 (session_e191_v2.sh, runner v2), refused unless step 8 v2's
# job a1-dry-e191-v2 ended rc 0 today (never the first session's a1-dry-e191), with THE RELAUNCH RULE in E192's G4 form (kit note 2,
# section 7): RB_OUT holds at most one session. When RB_OUT already holds a launch's T0 (e191-T0.txt), the box is read before anything
# launches: a launch that opened no device (its queue.json's t_first_ms null, a 'no device opened' line, no 'config start' line: no card
# command, card time 0, skipped by every rest rule) may be launched ONCE more from the same RB_OUT, inside the same window, every gate of
# this step passing again (the look reads FREE first: the brief's note); RB_OUT then holds e191-relaunch.txt, and a second refused launch
# ends the day (10, before any call). A launch that sent a card command is the RB_OUT's one session: refused (10). THE LAST LAUNCH (a gate
# made stricter for safety, added before the land after the note's verifier, its finding 2): right after k6's guard, before the rest rule,
# the box's last E191 launch (build/q141k/e191.T0, which every launch writes first) must be the last launch this RB_OUT knows: its
# e191-T0.txt, or, when it holds none, the first session's T0 1794766494 (1a4bc1e3); any other T0 is a launch that went out while its ssh
# call was lost (exit 14 before e191-T0.txt or e191-relaunch.txt was written): refused (10), nothing launched; read the box first, read
# only (step 10 v2 makes the same comparison: RUN-UNKNOWN). Every other line is
# v1's. v1's header: E191, the box step "the session" (this file
# is s11): E191's card session on aifoundry1 card 1, launched detached on the box (it returns at once), ONLY after steps 4-8 read clean (on
# a day with a post, after the post). E189's step 9 (tools/claims-v3/e189/rb/s11_a3_session_e189.sh, unchanged beside it) with E191's box:
# the window rule (written today for E191), the last start, the session's cap of 110 card-minutes before the last end (6,600 s), k6's guard
# (rb_guard_text: no dry pass running, no card session of ours on aifoundry1 by E191's ours_live, either card, and aifoundry1 booted before
# E82's firmware read of record), THE REST RULE (rb/rest_rule_e191.sh: every session-log form of ours in every tree of ours on aifoundry1,
# E190 arm B's among them; a session cut mid-queue counted at its run's latest write), today's dry pass (a1-dry-e191 ended rc 0 today) and
# today's build (the programs in RB_OUT/e191-built.txt, step 6's wait), then session_e191.sh detached (ET_DEVICES=1 in its environment and
# the runner's) with the T0 written on the box (build/q141k/e191.T0) and in RB_OUT (e191-T0.txt), which steps 10 and 11 read.
# --rapl-allowed only when his go allows a read of the host's package counter (default no).
#   bash tools/claims-v3/e191/rb/s11_a1_session_e191.sh FULL [--rapl-allowed]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e191.sh"
rb_init s11_a1_session_v2
plan=${1:-}
[ "$plan" = FULL ] || rb_die $RB_E_USAGE "E191 has one plan: FULL (the registered session; E191.md sections 9-10)"
rapl=""; [ "${2:-}" = --rapl-allowed ] && rapl=yes
e191_window
rb_need_start
rb_need_end "$E191_BUDGET_S"
prog=$(e191_programs)
[ -n "${RB_DRY:-}" ] && prog=${prog:-ledger,spp}
[ -n "$prog" ] || rb_die $RB_E_USAGE "no program was built today (RB_OUT/e191-built.txt, step 6's wait): run step 6 first"
prev=; [ -f "$RB_OUT/e191-T0.txt" ] && prev=$(cat "$RB_OUT/e191-T0.txt")
[ -n "$prev" ] && [ -f "$RB_OUT/e191-relaunch.txt" ] && rb_die $RB_E_USAGE "this RB_OUT has launched twice already (T0 $prev after $(head -c 10 "$RB_OUT/e191-relaunch.txt")): a second refused launch ends the day (kit note 2's relaunch rule); no launch"
E191_FIRST_T0=1794766494          # the first session's T0 (1a4bc1e3: 10:14:54 PST Sun 15 Nov 2026), the box's last E191 launch before A1's
f=$(rb_file e191)
{ rb_prelude aifoundry1
  echo "PROG=$prog; DEADLINE=${RB_LAST_END_EPOCH:-0}; RAPL=$rapl; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}"); PREV=$prev; FIRST=$E191_FIRST_T0"
  rb_guard_text
  cat <<'EOF2'
if [ -n "$PREV" ]; then KNOWN=$PREV; KW="this RB_OUT's e191-T0.txt"; else KNOWN=$FIRST; KW="the first session's T0 (1a4bc1e3; this RB_OUT has launched nothing)"; fi
LASTT0=$(cat build/q141k/e191.T0 2>/dev/null)     # kit note 2: THE LAST LAUNCH, before the rest rule (the note's verifier, finding 2)
if [ -z "$LASTT0" ] || [ "$LASTT0" != "$KNOWN" ]; then
  echo "REFUSED: the box's last E191 launch (build/q141k/e191.T0) reads ${LASTT0:-nothing}, not $KNOWN, $KW: a launch went out that this RB_OUT did not record (its ssh call lost after it). Read the box, read-only, before anything else; no launch"; exit 3
fi
echo "last launch: the box's build/q141k/e191.T0 reads $LASTT0, $KW"
EOF2
  cat "$RB_E191_DIR/rest_rule_e191.sh"
  cat <<'EOF2'
if [ -n "$PREV" ]; then          # kit note 2: the relaunch rule (E192's G4 form): only a launch that opened no device
  PD=build/e191/T$PREV
  if [ -f "$PD/queue.json" ] && grep -q '"t_first_ms": null' "$PD/queue.json" && grep -q 'no device opened' "$PD/session.log" 2>/dev/null && ! grep -q ' config start: ' "$PD/session.log" 2>/dev/null; then
    echo "relaunch: this RB_OUT's launch T0 $PREV opened no device (no card command, card time 0: $(grep -m1 'no device opened' "$PD/session.log" | cut -c25-180)): one launch more (kit note 2's relaunch rule)"
  else
    echo "REFUSED: this RB_OUT's launch T0 $PREV sent a card command, or cannot be read as a launch that opened no device: one session an RB_OUT; A1's second session is the day's last"; exit 3
  fi
fi
job_ok_today a1-dry-e191-v2 || { echo "REFUSED: E191's dry pass of runner v2 (step 8 v2's job a1-dry-e191-v2) has not ended rc 0 today"; exit 3; }
echo "dry pass: a1-dry-e191-v2 ended rc 0 today"
for p in ${PROG//,/ }; do
  case "$p" in ledger) w='^LEDGER-BUILT rc=0' ;; spp) w='^SPP-BUILT rc=0' ;; *) echo "REFUSED: unknown program $p"; exit 3 ;; esac
  fresh build/q141k/jobs/a1-build-e191.out && grep -q "$w" build/q141k/jobs/a1-build-e191.out ||
    { echo "REFUSED: $p was not built today (step 6's job a1-build-e191)"; exit 3; }
done
mkdir -p build/e191 build/q141k
T0=$(date +%s)
echo "$T0" > build/q141k/e191.T0
E191_T0=$T0 E191_PROGRAMS="$PROG" E191_DEADLINE_EPOCH="$DEADLINE" E191_RAPL="$RAPL" ET_DEVICES=1 V3_DEVICE=1 setsid nohup bash tools/claims-v3/e191/session_e191_v2.sh > build/e191/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e191 T0 $T0 $(date '+%F %T %Z') (session v2, kit note 2; programs $PROG; last start $LAST_START, last end $LAST_END; package counter: ${RAPL:-not read})"
tail -n 6 "build/e191/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry1
rb_remote launch aifoundry1 "launch e191, detached (programs $prog)" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e191
rb_has '^last launch: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^last launch: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^relaunch: ' && { echo "$prev $(grep -m1 '^relaunch: ' "$RB_CAP")" > "$RB_OUT/e191-relaunch.txt"; echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^relaunch: ' "$RB_CAP")" >> "$RB_LOG"; }
t0=$(rb_val '^LAUNCHED e191 T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e191-T0.txt"
rb_say "e191 (session v2, kit note 2) launched on aifoundry1 card 1 (programs $prog, T0 $t0); wait with s20_wait_e191_v2.sh (bounded), and read its identity lines, stop-path test and smoke gate"
