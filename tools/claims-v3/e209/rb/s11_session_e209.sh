#!/usr/bin/env bash
# E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): runbook step 9, THE SESSION (this file is s11, E200's name for step
# 9): E209's one session on aifoundry2 card 0, E208's runner unchanged, started detached by the box root's src/start_e209.sh.
#   RB_OUT=... E209_ROOT=... RB_QUIET=... RB_LANE=... RB_RELEASES=... bash tools/claims-v3/e209/rb/s11_session_e209.sh
# Refusals (10 unless said; nothing started): the window's last start passed; THE QUIET DESK FLAG not up or not the card lane's; no stamp
# from step 7 (RB_OUT/e209-first.txt) or one over 120 s old (step 7 again); THE REST RULE not open (17); fwgate.py guard over step 7's
# folder not "identity ... ok" (16, IDENTITY-STOP); a session, a build or a dry pass of the kit running, or THE P2 COUNT not 0 (17); an
# E209 session of today that reached the card already; then start_e209.sh's own refusals (3 -> 10: its words).
# On STARTED: RB_OUT/e209-session.txt "SID=<T0>-a2c0-E209". Exits: 0 started; 10, 16, 17 as above.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e209.sh"
rb_init s11_session
e209_window
NOW=$(rb_now)
[ "$NOW" -le "$E209_LAST_START" ] || rb_die 10 "past the last start ($(rb_pst -d "@$E209_LAST_START")): no session today"
e209_quiet_ours
rb_root
e209_rel_args
[ -f "$RB_OUT/e209-first.txt" ] || rb_die 10 "no stamp from step 7 in this RB_OUT"
# shellcheck disable=SC1091
. "$RB_OUT/e209-first.txt"
[ $((NOW - FIRST)) -le "$E209_FIRST_MAX_S" ] || rb_die 10 "the first card command was $((NOW - FIRST)) s ago, more than $E209_FIRST_MAX_S s: step 7 again"
[ -d "$E209_ROOT/$FIRSTDIR" ] || rb_die 10 "step 7's folder $FIRSTDIR is missing"
"$PY" -I -B "$RB_REPO/$E209_REL/rb/rest_rule_e209.py" --lab "$RB_REPO" --root "$E209_ROOT" "${REL_ARGS[@]}" > "$RB_OUT/rest-9.txt" 2>&1
rc=$?
tail -n 1 "$RB_OUT/rest-9.txt"
case "$rc" in 0) ;; 17) rb_die 17 "$(tail -n 1 "$RB_OUT/rest-9.txt")" ;; *) rb_die 16 "$(tail -n 1 "$RB_OUT/rest-9.txt")" ;; esac
GD=$(e209_fwgate guard --box aifoundry2 --card 0 --extra "$E209_ROOT/$FIRSTDIR" 2>&1); GRC=$?
echo "fwgate guard: rc $GRC: $(echo "$GD" | tail -n 1)"
[ "$GRC" -eq 0 ] || rb_die 16 "IDENTITY-STOP: $(echo "$GD" | tail -n 1): nothing launched"
e209_box_free || rb_die 17 "a session, a build or a dry pass of the kit runs in the box root: call again"
p2_count; [ "$P2_N" -eq 0 ] || rb_die 17 "THE P2 COUNT is $P2_N: call again (never kill one)"
TODAY=$(e209_session_today)
echo "$TODAY" | grep -q ' yes$' && rb_die 10 "an E209 session of today reached the card already: one session a day"
OUT=$(cd "$E209_ROOT" && env -u ET_DEVICES -u V3_DEVICE -u MMS_BOX_LOCK_FD E209_QUIET_FILE="$RB_QUIET" E209_QUIET_LANE="$RB_LANE" \
  timeout 120 bash src/start_e209.sh "$E209_LAST_END" "$FIRST" 2>&1); rc=$?
echo "$OUT" | tee "$RB_OUT/start.txt"
[ "$rc" -eq 0 ] || rb_die 10 "start_e209.sh refused (rc $rc): $(echo "$OUT" | grep -m1 REFUSED)"
SID=$(echo "$OUT" | grep -oE '^STARTED( DESKTEST)? [0-9]+-a2c0-E209' | awk '{print $NF}')
[ -n "$SID" ] || rb_die 14 "no STARTED line from start_e209.sh"
echo "SID=$SID" > "$RB_OUT/e209-session.txt"
rb_ok "STARTED $SID (wait with rb/s20_wait_e209.sh)"
