#!/usr/bin/env bash
# E224 (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum; E209's kit's rb/s11_session_e209.sh form): runbook step 9, THE SESSION (this file is s11, E200's name for step
# 9): E224's one session on aifoundry2 card 0 (src/run_e224b.py: E208's runner unchanged and imported, E224's lines and family G),
# started detached by the box root's src/start_e224b.sh.
#   RB_OUT=... E224B_ROOT=... RB_QUIET=... RB_LANE=... RB_RELEASES=... bash tools/claims-v3/e224/rb/s11_session_e224b.sh
# Refusals (10 unless said; nothing started): the window's last start passed; THE QUIET DESK FLAG not up or not the card lane's; no stamp
# from step 7 (RB_OUT/e224b-first.txt) or one over 120 s old (step 7 again); THE REST RULE not open (17); fwgate.py guard over step 7's
# folder not "identity ... ok" (16, IDENTITY-STOP); a session, a build or a dry pass of the kit running, or THE P2 COUNT not 0 (17); an
# E224 session of today that reached the card already; THE CPU RULE (fix-e216: 17 while the 1-minute load is 6 or more, right before the
# launch); then start_e224b.sh's own refusals (3 -> 10: its words).
# On STARTED: RB_OUT/e224b-session.txt "SID=<T0>-a2c0-E224". Exits: 0 started; 10, 16, 17 as above.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e224b.sh"
rb_init s11_session
e224b_window
NOW=$(rb_now)
[ "$NOW" -le "$E224B_LAST_START" ] || rb_die 10 "past the last start ($(rb_pst -d "@$E224B_LAST_START")): no session today"
e224b_quiet_ours
rb_root
e224b_rel_guard
e224b_rel_args
[ -f "$RB_OUT/e224b-first.txt" ] || rb_die 10 "no stamp from step 7 in this RB_OUT"
# shellcheck disable=SC1091
. "$RB_OUT/e224b-first.txt"
[ $((NOW - FIRST)) -le "$E224B_FIRST_MAX_S" ] || rb_die 10 "the first card command was $((NOW - FIRST)) s ago, more than $E224B_FIRST_MAX_S s: step 7 again"
[ -d "$E224B_ROOT/$FIRSTDIR" ] || rb_die 10 "step 7's folder $FIRSTDIR is missing"
"$PY" -I -B "$RB_REPO/$E224B_REL/rb/rest_rule_e224b.py" --lab "$RB_REPO" --root "$E224B_ROOT" "${REL_ARGS[@]}" > "$RB_OUT/rest-9.txt" 2>&1
rc=$?
tail -n 1 "$RB_OUT/rest-9.txt"
case "$rc" in 0) ;; 17) rb_die 17 "$(tail -n 1 "$RB_OUT/rest-9.txt")" ;; *) rb_die 16 "$(tail -n 1 "$RB_OUT/rest-9.txt")" ;; esac
GD=$(e224b_fwgate guard --box aifoundry2 --card 0 --extra "$E224B_ROOT/$FIRSTDIR" 2>&1); GRC=$?
echo "fwgate guard: rc $GRC: $(echo "$GD" | tail -n 1)"
[ "$GRC" -eq 0 ] || rb_die 16 "IDENTITY-STOP: $(echo "$GD" | tail -n 1): nothing launched"
e224b_box_free || rb_die 17 "a session, a build or a dry pass of the kit runs in the box root: call again"
p2_count; [ "$P2_N" -eq 0 ] || rb_die 17 "THE P2 COUNT is $P2_N: call again (never kill one)"
TODAY=$(e224b_session_today)
echo "$TODAY" | grep -q ' yes$' && rb_die 10 "an E224 session of today reached the card already: one session a day"
# fix-e216 (verify-e216's F8): THE CPU RULE's launch gate, right before the launch (17: nothing launched; call again within the stamp's 120 s)
e224b_load_gate "step 9, before the launch"
OUT=$(cd "$E224B_ROOT" && env -u ET_DEVICES -u V3_DEVICE -u MMS_BOX_LOCK_FD E224B_QUIET_FILE="$RB_QUIET" E224B_QUIET_LANE="$RB_LANE" \
  timeout 120 bash src/start_e224b.sh "$E224B_LAST_END" "$FIRST" 2>&1); rc=$?
echo "$OUT" | tee "$RB_OUT/start.txt"
[ "$rc" -eq 0 ] || rb_die 10 "start_e224b.sh refused (rc $rc): $(echo "$OUT" | grep -m1 REFUSED)"
SID=$(echo "$OUT" | grep -oE '^STARTED( DESKTEST)? [0-9]+-a2c0-E224' | awk '{print $NF}')
[ -n "$SID" ] || rb_die 14 "no STARTED line from start_e224b.sh"
echo "SID=$SID" > "$RB_OUT/e224b-session.txt"
rb_ok "STARTED $SID (wait with rb/s20_wait_e224b.sh)"
