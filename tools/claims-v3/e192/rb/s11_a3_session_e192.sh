#!/usr/bin/env bash
# E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum), the box step "the session" (this file is s11): E192's card session on
# aifoundry3, launched detached on the box (it returns at once), ONLY after steps 1-8 read clean. E189's step 9 form
# (rb/s11_a3_session_e189.sh): the window rule (written today for E192), the last start, the session's cap of 65 card-minutes before the
# last end (3,900 s), k6's guard (no dry pass running, no card session of ours: rb_guard_text), THE REST RULE (rb/rest_rule_e192.sh: every
# session-log form of ours on the box; 40 minutes, refused before it), today's dry pass (a3-dry-e192 ended rc 0 today) and today's build
# (a3-build-e192 built today, RB_OUT/e192-built.txt), then session_e192.sh detached (setsid nohup) with the T0 written on the box
# (build/q141k/e192.T0) and in RB_OUT (e192-T0.txt), which steps 10 and 11 read, the window's last end and the kit list's sha256 (the
# session checks the box's copy against it). --plain-sampler only when his go names the plain sampler (E192_SAMPLER=ettelem: no probe).
#   bash tools/claims-v3/e192/rb/s11_a3_session_e192.sh FULL [--plain-sampler]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e192.sh"
rb_init s11_a3_session
plan=${1:-}
[ "$plan" = FULL ] || rb_die $RB_E_USAGE "E192 has one plan: FULL (the registered session: the smoke and 9 passes; E192.md sections 5 and 10)"
plain=""; [ "${2:-}" = --plain-sampler ] && plain=ettelem
e192_window
rb_need_start
rb_need_end "$E192_BUDGET_S"
[ -n "${RB_DRY:-}" ] || [ -n "$(e192_built)" ] || rb_die $RB_E_USAGE "E192 was not built today (RB_OUT/e192-built.txt, step 6's wait): run step 6 first"
KLS=$(e192_kitlist_sha)
[ -n "${RB_DRY:-}" ] || [ -n "$KLS" ] || rb_die $RB_E_USAGE "no kit list in the lab clone"
f=$(rb_file e192)
{ rb_prelude aifoundry3
  echo "ER=$E192_R; DEADLINE=${RB_LAST_END_EPOCH:-0}; KLS=$KLS; PLAIN=$plain; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E192_DIR/rest_rule_e192.sh"
  cat <<'EOF2'
job_ok_today a3-dry-e192 || { echo "REFUSED: E192's dry pass (step 8's job a3-dry-e192) has not ended rc 0 today"; exit 3; }
echo "dry pass: a3-dry-e192 ended rc 0 today"
fresh build/q141k/jobs/a3-build-e192.out && grep -q '^INTBITS-BUILT rc=0' build/q141k/jobs/a3-build-e192.out ||
  { echo "REFUSED: E192 was not built today (step 6's job a3-build-e192)"; exit 3; }
mkdir -p build/e192 build/q141k
T0=$(date +%s)
echo "$T0" > build/q141k/e192.T0
if [ -n "$PLAIN" ]; then
  E192_SAMPLER=ettelem E192_T0=$T0 E192_DEADLINE_EPOCH="$DEADLINE" E192_KITLIST_SHA256="$KLS" setsid nohup bash "$ER/tools/claims-v3/e192/session_e192.sh" > "build/e192/launch-T$T0.out" 2>&1 < /dev/null &
else
  E192_T0=$T0 E192_DEADLINE_EPOCH="$DEADLINE" E192_KITLIST_SHA256="$KLS" setsid nohup bash "$ER/tools/claims-v3/e192/session_e192.sh" > "build/e192/launch-T$T0.out" 2>&1 < /dev/null &
fi
sleep 5
echo "LAUNCHED e192 T0 $T0 $(date '+%F %T %Z') (last start $LAST_START, last end $LAST_END; sampler: ${PLAIN:-the per-sensor probe decides})"
tail -n 8 "build/e192/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e192, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e192
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
t0=$(rb_val '^LAUNCHED e192 T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e192-T0.txt"
rb_say "e192 launched on aifoundry3 (T0 $t0); wait with s20_wait_e192.sh (bounded), and read its smoke gate and the cap"
