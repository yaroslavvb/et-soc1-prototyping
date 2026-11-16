#!/usr/bin/env bash
# E197 (Q185, the kit), the box step "the reads" (this file is s09; k6's step 7, wrapped), ONE SITTING A CALL. k6's reads
# (tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh, called UNCHANGED as a child: et-lab-manifest kept on the box, the card's static
# config through E128's guard under the card lock with timeout 10 -- TDP 0 W, 65 C, 600 MHz as found, never set -- and et-who's holder
# rule) send five READs to the card's management node: on E197's day THAT CONFIG READ IS THE SITTING'S FIRST CARD COMMAND (E197.md 6:
# "the first command of the sitting that reaches the card or its management node (a configuration read included) or the sitting's
# first holder check, whichever comes first"; the session's holder checks come later; k6's look, step 4, sends nothing to the card).
# E192's data note 1 found a step 7 read inside the rest; so this wrapper, BEFORE anything reaches the card:
#   1. the window rule (written today for E197 and this sitting) and the last start (the first card command is the sitting's start,
#      E197.md 12);
#   2. today's build (RB_OUT/e197-built.txt, step 6) and today's dry pass for this sitting (RB_OUT/e197-<n>-dry-ok.txt, step 8): the
#      order is 5, 6, 8, then 7 once the rest has opened, then 9 at once (CARD-LANE-BRIEF.md 2);
#   3. on the box, read only: no card session of ours and no runbook job running; THE REST RULE (rb/rest_rule_e197.sh: at least 40
#      minutes since the end of our last real session on the card, every session-log form of ours read); for sitting 2, SITTING 1 HELD
#      FIRST (a real E197 sitting-1 log on the box that ended, whose SITTING-RESULT reads smoke passed, at least one train block complete
#      and no card stop: E197.md 6; else a dated amendment first) and no crashed sitting 1;
#   4. the plan, decided at the first card command and logged (E197.md 6, the lab's reading): sitting 1 the full plan when the time
#      left to the last end holds its cap (3,000 s) and the kit's closing steps (900 s), else the short plan (2,400 s + 900 s), else no
#      sitting that day (16); sitting 2 the ext plan (2,100 s + 900 s), else 16;
#   5. the first card command stamped (epoch, just before k6's call: no command of this sitting reaches the card before it) into
#      RB_OUT/e197-<n>-first.txt (FIRST=, PLAN=, REST=), ONCE A SITTING: a second call keeps the first stamp and its plan (step 7 again
#      after its 17, say: the cap and the rest count from the first);
#   6. k6's s09, its exit passed through (0 the config as found and et-who clean; 16 the config is not TDP 0 W / 65 C / 600 MHz or none
#      came back: no sitting that day, set nothing; 17 et-who not clean: look again with --wait, then this step again).
# Step 9 must follow within 2 minutes (E197_FIRST_MAX_S; it refuses after: the cap counts from the stamp).
#   bash tools/claims-v3/e197/rb/s09_a3_reads_e197.sh 1|2
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e197.sh"
rb_init s09_a3_reads
sit=${1:-}
e197_sit_ok "$sit" || rb_die $RB_E_USAGE "usage: s09_a3_reads_e197.sh 1|2 (the sitting this RB_OUT's window names)"
e197_window "$sit"
rb_need_start
[ -n "${RB_DRY:-}" ] || e197_built_today || rb_die $RB_E_USAGE "regfile was not built today (RB_OUT/e197-built.txt, step 6's wait): run step 6 first"
[ -n "${RB_DRY:-}" ] || [ -f "$RB_OUT/e197-$sit-dry-ok.txt" ] ||
  rb_die $RB_E_USAGE "no dry pass ended rc 0 today for sitting $sit in this RB_OUT (step 8's wait): run step 8 first"
[ -n "${RB_DRY:-}" ] || [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e197-$sit-dry-ok.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
  rb_die $RB_E_USAGE "the dry pass record for sitting $sit was not written today: run step 8 first"
FF=$RB_OUT/e197-$sit-first.txt
if [ -z "${RB_DRY:-}" ] && [ -f "$FF" ]; then
  E197_SIT=$sit
  e197_first || rb_die $RB_E_USAGE "$FF exists but does not read FIRST= and PLAN=: read it"
  [ "$(TZ=America/Los_Angeles e197_fmt "$E197_FIRST" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "$FF is not today's: one RB_OUT per sitting and day"
  echo "$(date '+%F %T %Z') step=$RB_STEP again: the sitting's first card command stays $(e197_fmt "$E197_FIRST" '+%T %Z') (plan $E197_PLAN_CHOSEN)" >> "$RB_LOG"
  rb_say "step 7 again for sitting $sit: the first card command stays at the first stamp (FIRST $E197_FIRST, plan $E197_PLAN_CHOSEN); k6's reads follow"
else
  rb_probe aifoundry3
  f=$(rb_file rest)
  { rb_prelude aifoundry3
    echo "SIT=$sit"
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: the reads wait"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: the reads wait"; exit 3; fi
EOF2
    cat "$RB_E197_DIR/rest_rule_e197.sh"
    cat <<'EOF2'
if [ "$SIT" = 2 ]; then
  a=""; cr=""; why=""
  for L in build/e197/T[0-9]*/session.log; do
    [ -f "$L" ] || continue
    case "$L" in *-dry*) continue ;; esac
    grep -q 'E197 sitting 1,' "$L" && grep -q 'session end' "$L" || continue
    if grep -q 'the trains ended without a registered stop' "$L"; then cr=$L; continue; fi
    r=$(grep -m1 'SITTING-RESULT: ' "$L" | sed 's/.*SITTING-RESULT: //')
    case "$r" in "smoke passed; train blocks complete "[1-9]*"card stop none") a=$L ;; *) why="$why ${L%/session.log}: ${r:-no SITTING-RESULT}" ;; esac
  done
  [ -z "$cr" ] || { echo "REFUSED: E197 sitting 1 ended without a registered stop (a crash: ${cr%/session.log}): no sitting 2 before a dated note decides"; exit 3; }
  [ -n "$a" ] || { echo "REFUSED: no E197 sitting 1 on this box that ran its smoke and at least one train block with no stop naming the card (E197.md 6:${why:- none found}): sitting 2 needs a dated amendment"; exit 3; }
  echo "sitting 1 held first: ${a%/session.log}"
fi
echo "READS-MAY-FOLLOW"
EOF2
  } > "$f"
  rb_remote read aifoundry3 "before the first card command: nothing of ours running, the rest rule, sitting 1 first (sitting 2)" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the reads exited $RB_RC: nothing sent to the card"
  rest=$(rb_val '^(rest: .*)$')
  [ -n "${RB_DRY:-}" ] || rb_has '^READS-MAY-FOLLOW' || rb_die $RB_E_FAIL "the read before the reads gave no answer: nothing sent to the card"
  rb_window
  left=$((RB_LAST_END_EPOCH - RB_NOW))
  if [ "$sit" = 1 ]; then
    if [ "$left" -ge $(( $(e197_cap_s full) + E197_CLOSE_S )) ]; then plan=full
    elif [ "$left" -ge $(( $(e197_cap_s short) + E197_CLOSE_S )) ]; then plan=short
    else plan=""; fi
  else
    plan=""; [ "$left" -ge $(( $(e197_cap_s ext) + E197_CLOSE_S )) ] && plan=ext
  fi
  [ -n "${RB_DRY:-}" ] && plan=${plan:-full}
  [ -n "$plan" ] || rb_die $RB_E_GATE "$((left / 60)) minutes to the last end hold no plan's cap and the closing steps: no sitting $sit today (nothing sent to the card)"
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- the plan decided now and logged (sitting 1: full if the cap 3,000 s + 900 s fit before the last end, else short if 2,400 s + 900 s, else no sitting; sitting 2: ext, 2,100 s + 900 s); the first card command stamped into <RB_OUT>/e197-$sit-first.txt"
  else
    FIRST=$(date +%s)
    { echo "FIRST=$FIRST"; echo "PLAN=$plan"; echo "REST=${rest:-}"; echo "AT=$(e197_fmt "$FIRST" '+%F %T %Z')"; } > "$FF"
    echo "$(date '+%F %T %Z') step=$RB_STEP the first card command of sitting $sit stamped $FIRST (plan $plan; $rest)" >> "$RB_LOG"
    rb_say "sitting $sit: $rest; the plan: $plan; the first card command stamped now ($(e197_fmt "$FIRST" '+%T %Z')): k6's reads follow"
  fi
fi
bash "$RB_REPO/tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh"
rc=$?
[ -n "${RB_DRY:-}" ] && exit "$rc"
case "$rc" in
  0) rb_say "k6's reads: the config as found and et-who clean; run step 9 now (within $((E197_FIRST_MAX_S / 60)) minutes of the first card command)" ;;
  17) rb_say "k6's reads: et-who not clean: look again (s05_look_k6.sh aifoundry3 --wait), then this step again (the first card command stays) and step 9 within $((E197_FIRST_MAX_S / 60)) minutes of it, else a new RB_OUT (steps 1, 6's wait, 8, then 7)" ;;
  *) rb_say "k6's reads ended $rc: read its lines above (16: no sitting $sit today, set nothing)" ;;
esac
exit "$rc"
