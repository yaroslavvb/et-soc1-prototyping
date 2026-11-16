#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum; E192's file, a6fe5c20, unchanged beside it, ported to aifoundry1 card 1), the box step "the session" (this file is s11): E199's card session on
# aifoundry1, launched detached on the box (it returns at once), ONLY after steps 1-8 read clean. E189's step 9 form
# (rb/s11_a3_session_e189.sh): the window rule (written today for E199), the last start, the session's cap of 65 card-minutes before the
# last end (3,900 s), k6's guard (no dry pass running, no card session of ours: rb_guard_text), THE REST RULE (rb/rest_rule_e199.sh: every
# session-log form of ours on the box; 40 minutes, refused before it), today's dry pass (a1-dry-e199 ended rc 0 today) and today's build
# (a1-build-e199 built today, RB_OUT/e199-built.txt), then session_e199.sh detached (setsid nohup) with the T0 written on the box
# (build/q141k/e199.T0) and in RB_OUT (e199-T0.txt), which steps 10 and 11 read, the window's last end and the kit list's sha256 (the
# session checks the box's copy against it). --plain-sampler only when his go names the plain sampler (E199_SAMPLER=ettelem: no probe).
#   bash tools/claims-v3/e199/rb/s11_a1_session_e199.sh FULL [--plain-sampler]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e199.sh"
rb_init s11_a1_session
plan=${1:-}
[ "$plan" = FULL ] || rb_die $RB_E_USAGE "E199 has one plan: FULL (the registered session: the smoke and 9 passes; E199.md sections 5 and 10)"
plain=""; [ "${2:-}" = --plain-sampler ] && plain=ettelem
e199_window
rb_need_start
rb_need_end "$E199_BUDGET_S"
[ -n "${RB_DRY:-}" ] || [ -n "$(e199_built)" ] || rb_die $RB_E_USAGE "E199 was not built today (RB_OUT/e199-built.txt, step 6's wait): run step 6 first"
KLS=$(e199_kitlist_sha)
[ -n "${RB_DRY:-}" ] || [ -n "$KLS" ] || rb_die $RB_E_USAGE "no kit list in the lab clone"
f=$(rb_file e199)
{ rb_prelude aifoundry1
  echo "ER=$E199_R; DEADLINE=${RB_LAST_END_EPOCH:-0}; KLS=$KLS; PLAIN=$plain; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E199_DIR/rest_rule_e199.sh"
  cat <<'EOF2'
job_ok_today a1-dry-e199 || { echo "REFUSED: E199's dry pass (step 8's job a1-dry-e199) has not ended rc 0 today"; exit 3; }
echo "dry pass: a1-dry-e199 ended rc 0 today"
fresh build/q141k/jobs/a1-build-e199.out && grep -q '^INTBITS-BUILT rc=0' build/q141k/jobs/a1-build-e199.out ||
  { echo "REFUSED: E199 was not built today (step 6's job a1-build-e199)"; exit 3; }
mkdir -p build/e199 build/q141k
T0=$(date +%s)
echo "$T0" > build/q141k/e199.T0
if [ -n "$PLAIN" ]; then
  E199_SAMPLER=ettelem E199_T0=$T0 E199_DEADLINE_EPOCH="$DEADLINE" E199_KITLIST_SHA256="$KLS" setsid nohup bash "$ER/tools/claims-v3/e199/session_e199.sh" > "build/e199/launch-T$T0.out" 2>&1 < /dev/null &
else
  E199_T0=$T0 E199_DEADLINE_EPOCH="$DEADLINE" E199_KITLIST_SHA256="$KLS" setsid nohup bash "$ER/tools/claims-v3/e199/session_e199.sh" > "build/e199/launch-T$T0.out" 2>&1 < /dev/null &
fi
sleep 5
echo "LAUNCHED e199 T0 $T0 $(date '+%F %T %Z') (last start $LAST_START, last end $LAST_END; sampler: ${PLAIN:-the per-sensor probe decides})"
tail -n 8 "build/e199/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry1
rb_remote launch aifoundry1 "launch e199, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e199
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
t0=$(rb_val '^LAUNCHED e199 T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e199-T0.txt"
rb_say "e199 launched on aifoundry1 (T0 $t0); wait with s20_wait_e199.sh (bounded), and read its smoke gate and the cap"
