#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum), the box step "the session" (this file is s11): E202's card session on
# aifoundry3, launched detached on the box (it returns at once), ONLY after steps 5-8 read clean. E189's step 9 form
# (tools/claims-v3/e189/rb/s11_a3_session_e189.sh): the window rule (written today for E202), the last start, the session's cap of 35
# card-minutes before the last end (2,100 s), k6's guard (no dry pass running, no card session of ours: rb_guard_text), THE REST RULE
# (rb/rest_rule_e202.sh: every session-log form of ours, a session cut mid-queue counted at its run's latest write), THE SAME-DAY RULE (the
# kit's, E196's form: an E202 session that opened the card today is never launched again that day; a launch that ended "refused, no device
# opened" may be launched once more, two such a day at most), today's dry pass (a3-dry-e202 ended rc 0 today) and today's build (E202-BUILT
# in a3-build-e202's output today), then session_e202.sh detached with the T0 written on the box (build/q141k/e202.T0) and in RB_OUT
# (e202-T0.txt), which steps 10 and 11 read, and the window's last end as its deadline.
# THE HUNG MARKER (fix-e202, verify-e202's note 11): before the launch, every session log of ours on the box (any *.log under build/,
# the dry paths aside) is read for a HUNG marker (E197's kit writes "<time> HUNG: ..." when a device process of ours did not end after
# its timeout's TERM; any kit's line stamped at its start and saying HUNG counts): one found refuses the launch (10): the card may hold
# a hung hart. Only the owner's word and a dated kit amendment lift it; a live hung process also fails k6's holder rule at steps 4 and 7.
#   bash tools/claims-v3/e202/rb/s11_a3_session_e202.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e202.sh"
rb_init s11_a3_session
e202_window
rb_need_start
rb_need_end "$E202_BUDGET_S"
[ -n "${RB_DRY:-}" ] || [ -n "$(e202_built)" ] || rb_die $RB_E_USAGE "E202 was not built today (RB_OUT/e202-built.txt, step 6's wait): run step 6 first"
f=$(rb_file e202)
{ rb_prelude aifoundry3
  echo "DEADLINE=${RB_LAST_END_EPOCH:-0}; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E202_DIR/rest_rule_e202.sh"
  cat <<'EOF2'
hung=$(grep -r -H -m1 -E --include='*.log' --exclude-dir='*-dry*' --exclude-dir='*dry-t*' \
  '^[0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9]{2}:[0-9]{2}:[0-9]{2}([^ ]*)( [A-Z]+)? HUNG[: ]' build 2>/dev/null | head -n 3)
[ -z "$hung" ] || { echo "REFUSED: a HUNG marker of ours on the box ($(printf '%s\n' "$hung" | head -n 1 | cut -c1-220)): a device process of ours did not end after its timeout's TERM, so the card may hold a hung hart: stop and report to the owner; only his word and a dated kit amendment lift this (fix-e202)"; exit 3; }
echo "hung: no HUNG marker in our session logs on the box"
TODAY=$(TZ=America/Los_Angeles date +%F)
opened=0; nodev=0
for L in build/e202/T[0-9]*/session.log; do
  [ -f "$L" ] || continue
  case "$L" in *-dry*) continue ;; esac
  [ "$(TZ=America/Los_Angeles date -r "$L" +%F)" = "$TODAY" ] || continue
  if grep -q 'first card command' "$L"; then opened=$((opened + 1)); elif grep -q '^[-0-9]* [:0-9]* [A-Z]* refused, no device opened: ' "$L"; then nodev=$((nodev + 1)); fi
done
[ "$opened" -eq 0 ] || { echo "REFUSED: an E202 session opened the card today ($opened): never again the same day (the kit's same-day rule; a later try needs another day, or a dated amendment after data)"; exit 3; }
[ "$nodev" -lt 2 ] || { echo "REFUSED: $nodev E202 launches ended 'refused, no device opened' today: two such launches a day at most (the kit's same-day rule)"; exit 3; }
echo "same-day: no E202 session opened the card today; $nodev launch(es) refused before any card command today"
job_ok_today a3-dry-e202 || { echo "REFUSED: E202's dry pass (step 8's job a3-dry-e202) has not ended rc 0 today"; exit 3; }
echo "dry pass: a3-dry-e202 ended rc 0 today"
fresh build/q141k/jobs/a3-build-e202.out && grep -q '^E202-BUILT rc=0' build/q141k/jobs/a3-build-e202.out ||
  { echo "REFUSED: E202 was not built today (step 6's job a3-build-e202)"; exit 3; }
mkdir -p build/e202 build/q141k
T0=$(date +%s)
[ -e "build/e202/T$T0" ] && { sleep 1; T0=$(date +%s); }
echo "$T0" > build/q141k/e202.T0
E202_T0=$T0 E202_DEADLINE_EPOCH="$DEADLINE" setsid nohup bash tools/claims-v3/e202/session_e202.sh > build/e202/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e202 T0 $T0 $(date '+%F %T %Z') (last start $LAST_START, last end $LAST_END)"
tail -n 6 "build/e202/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e202, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e202
for w in rest hung same-day; do rb_has "^$w: " && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 "^$w: " "$RB_CAP")" >> "$RB_LOG"; done
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
t0=$(rb_val '^LAUNCHED e202 T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e202-T0.txt"
rb_say "e202 launched on aifoundry3 (T0 $t0); wait with s20_wait_e202.sh (bounded), and read its stop-path test and smoke gate"
