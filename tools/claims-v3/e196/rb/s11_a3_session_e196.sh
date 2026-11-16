#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum), the box step "the session" (this file is s11): E196's card session
# on aifoundry3, launched detached on the box (it returns at once), ONLY after steps 1-8 read clean. E192's step 9 form
# (tools/claims-v3/e192/rb/s11_a3_session_e192.sh) with E193's same-day rule: the window rule (written today for E196), the last start,
# the session's cap of 60 card-minutes before the last end (3,600 s), k6's guard (no dry pass running, no card session of ours:
# rb_guard_text), THE REST RULE (rb/rest_rule_e196.sh: every session-log form of ours on the box; 40 minutes, refused before it), today's
# dry pass (a3-dry-e196 ended rc 0 today) and today's build (a3-build-e196 built today, RB_OUT/e196-built.txt), THE SAME-DAY RULE (the
# kit's reading, for the go to confirm: E196 runs once a Pacific day; a launch that ended with "(no device opened)" sent no card command
# and may be launched once more the same day; a session that opened the card and ended at a gate (the opening configuration read, the
# smoke) is not tried again that day; a session with data is not run twice), then session_e196.sh detached (setsid nohup) with the T0
# written on the box (build/q141k/e196.T0) and in RB_OUT (e196-T0.txt), which steps 10 and 11 read, the window's last end and the kit
# list's sha256 (the session checks the box's copy against it).
#   bash tools/claims-v3/e196/rb/s11_a3_session_e196.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e196.sh"
rb_init s11_a3_session
[ $# -eq 0 ] || rb_die $RB_E_USAGE "usage: s11_a3_session_e196.sh (E196 has one plan: the registered session, E196.md section 6)"
e196_window
rb_need_start
rb_need_end "$E196_CAP_S"
[ -n "${RB_DRY:-}" ] || [ -n "$(e196_built)" ] || rb_die $RB_E_USAGE "E196 was not built today (RB_OUT/e196-built.txt, step 6's wait): run step 6 first"
KLS=$(e196_kitlist_sha)
[ -n "${RB_DRY:-}" ] || [ -n "$KLS" ] || rb_die $RB_E_USAGE "no kit list in the lab clone"
f=$(rb_file e196)
{ rb_prelude aifoundry3
  echo "ER=$E196_R; DEADLINE=${RB_LAST_END_EPOCH:-0}; KLS=$KLS; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat <<'EOF2'
TODAY=$(TZ=America/Los_Angeles date +%F); nodev=0
for L in build/e196/T[0-9]*/session.log; do
  [ -f "$L" ] || continue
  case "$L" in *-dry/*) continue ;; esac
  fresh "$L" || continue
  if grep -q 'no device opened' "$L"; then nodev=$((nodev + 1)); continue; fi
  if grep -q 'GATE-STOP:' "$L"; then echo "REFUSED: an E196 session opened the card today and ended at a gate ($L): no second try today (the kit's same-day rule)"; exit 3; fi
  echo "REFUSED: an E196 session ran today already ($L): never twice a day without a dated amendment"; exit 3
done
[ "$nodev" -lt 2 ] || { echo "REFUSED: two E196 launches today ended with no device opened: no third today (the kit's same-day rule)"; exit 3; }
echo "same day: $nodev earlier launch(es) today, each with no device opened"
EOF2
  cat "$RB_E196_DIR/rest_rule_e196.sh"
  cat <<'EOF2'
job_ok_today a3-dry-e196 || { echo "REFUSED: E196's dry pass (step 8's job a3-dry-e196) has not ended rc 0 today"; exit 3; }
echo "dry pass: a3-dry-e196 ended rc 0 today"
fresh build/q141k/jobs/a3-build-e196.out && grep -q '^E196-BUILT rc=0' build/q141k/jobs/a3-build-e196.out ||
  { echo "REFUSED: E196 was not built today (step 6's job a3-build-e196)"; exit 3; }
mkdir -p build/e196 build/q141k
T0=$(date +%s)
echo "$T0" > build/q141k/e196.T0
E196_T0=$T0 E196_DEADLINE_EPOCH="$DEADLINE" E196_KITLIST_SHA256="$KLS" setsid nohup bash "$ER/tools/claims-v3/e196/session_e196.sh" > "build/e196/launch-T$T0.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e196 T0 $T0 $(date '+%F %T %Z') (last start $LAST_START, last end $LAST_END)"
tail -n 8 "build/e196/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e196, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e196
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
t0=$(rb_val '^LAUNCHED e196 T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e196-T0.txt"
rb_say "e196 launched on aifoundry3 (T0 $t0); wait with s20_wait_e196.sh (bounded); read its smoke gate, the stops and how it ended"
