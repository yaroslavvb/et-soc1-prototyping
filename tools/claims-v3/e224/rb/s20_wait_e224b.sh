#!/usr/bin/env bash
# E224 (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum; E209's kit's rb/s20_wait_e209.sh form): runbook step 10, THE WAIT: the session found by its REAL script name
# as its own script (ours_live 'session_e224b.sh': an interpreter's first non-option argument, never a command string's text) and read by
# E208's src/status_mms.sh (unchanged: ENDED 0 with MANIFEST.sha256, RUNNING 17, GONE 14). Reads only; kills nothing, ever: a LEFTOVER (a
# device process of ours that outlived its TERM) is reported at once and left for the lab admin.
#   RB_OUT=... E224B_ROOT=... bash tools/claims-v3/e224/rb/s20_wait_e224b.sh       (bounded: at most 520 s a call; while 17, call again)
# Exits: 0 ENDED, runner rc 0 (the summary printed); 16 ENDED with runner rc 16 (a gate refused before any run: nothing measured, or the
# smoke gate) or with a LEFTOVER (tell the orchestrator; never kill -9), or GONE (no runner, no manifest: read session.log); 17 still
# running (call again); 10 no session in this RB_OUT.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e224b.sh"
rb_init s20_wait
rb_root
[ -f "$RB_OUT/e224b-session.txt" ] || rb_die 10 "no session started in this RB_OUT (step 9)"
# shellcheck disable=SC1091
. "$RB_OUT/e224b-session.txt"
D="$E224B_ROOT/sessions/$SID"
[ -d "$D" ] || rb_die 10 "no session folder $SID in the box root"
end=$(( $(rb_now) + E224B_BOUND_S ))
while :; do
  N=$(ours_live session_e224b.sh)
  ST=$(cd "$E224B_ROOT" && timeout 60 bash src/status_mms.sh a2c0 "$SID" 2>&1); SRC=$?
  if [ "$SRC" -eq 0 ]; then
    echo "$ST" | tail -n 12
    RC=$(cat "$D/runner.rc" 2>/dev/null || echo '?')
    if grep -q 'LEFTOVER' "$D/session.log" 2>/dev/null || grep -q '"leftover": {' "$D/queue.json" 2>/dev/null; then
      rb_die 16 "ENDED with a LEFTOVER ($(grep -m1 'LEFTOVER' "$D/session.log")): tell the orchestrator; kill nothing"
    fi
    [ "$RC" = 0 ] && rb_ok "ENDED: runner rc 0; $(tail -n 1 "$D/session.log" | cut -c1-160)"
    rb_die 16 "ENDED: runner rc $RC ($(grep -m1 -E 'gate|STOP|failed|refused' "$D/session.log" | cut -c1-160))"
  fi
  if [ "$SRC" -eq 14 ]; then
    echo "$ST" | tail -n 6
    rb_die 16 "GONE: no runner and no manifest (session_e224b.sh scripts of ours alive: $N): read $SID/session.log"
  fi
  [ "$SRC" -eq 17 ] || rb_die 14 "status_mms.sh ended rc $SRC: $(echo "$ST" | tail -n 1)"
  if grep -q 'LEFTOVER' "$D/session.log" 2>/dev/null; then
    echo "$(grep 'LEFTOVER' "$D/session.log" | tail -n 1)"
    echo "a LEFTOVER is recorded: the session holds the card's lock until no device process of ours is left (at most 10 minutes); kill nothing"
  fi
  echo "RUNNING ($(rb_pst)): session_e224b.sh scripts of ours by their own name: $N; $(echo "$ST" | sed -n 2,3p | tr '\n' ' ' | cut -c1-200)"
  [ "$(rb_now)" -lt "$end" ] || rb_die 17 "the session runs: call again"
  sleep 15
done
