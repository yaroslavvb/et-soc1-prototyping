#!/usr/bin/env bash
# E190 (Q169, the kit), the box step "the wait" (this file is s20), for one arm: one bounded wait on that arm's session (the session log of
# the T0 the runbook launched today on its box); each call ends within the remote loop's 520 s; call again while it says 17. It never
# touches the card. E189's step 10's form: the T0 is the launch's own (build/q141k/e190<arm>.T0, written today, the same as RB_OUT's
# e190-T0-<arm>.txt), its log build/e190/T<T0>-<arm>/session.log; when the session has ended, the wait also says whether its
# MANIFEST.sha256 is written (the exact copy-back reads it). A session that ended at a gate (the box or build check, the lock, a holder, the
# start config, the sampler, the stop-path test, the smoke) is 16, and step 11 still collects it (E184's lesson).
#   bash tools/claims-v3/e190/rb/s20_wait_e190.sh <A|B>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e190.sh"
rb_init s20_wait
e190_arm "${1:-}"
want=; [ -f "$RB_OUT/e190-T0-$ARM.txt" ] && want=$(cat "$RB_OUT/e190-T0-$ARM.txt")
[ -n "${RB_DRY:-}" ] || [ -n "$want" ] || rb_die $RB_E_USAGE "RB_OUT holds no e190-T0-$ARM.txt: step 9 has not launched E190's arm $ARM from this RB_OUT"
rb_probe "$BOX"
f=$(rb_file "wait-e190$ARM")
{ rb_prelude "$BOX"
  echo "ARM=$ARM; LIM=$RB_WAIT_LOOP_S; WANT='${want:-DRY}'"
  cat <<'EOF2'
fresh "build/q141k/e190$ARM.T0" || { echo "RUN-UNKNOWN e190 arm $ARM: not launched today by the runbook (no T0 written today)"; exit 3; }
T0=$(cat "build/q141k/e190$ARM.T0")
[ "$WANT" = DRY ] || [ "$T0" = "$WANT" ] || { echo "RUN-UNKNOWN e190 arm $ARM: the box's last launch T0 $T0 is not this runbook's $WANT"; exit 3; }
SD=build/e190/T$T0-$ARM; L=$SD/session.log
ended() { grep -q 'session end' "$L" 2>/dev/null; }
while ! ended && [ "$SECONDS" -lt "$LIM" ]; do
  [ "$(ours_live 'session_e190.sh')" -gt 0 ] || { sleep 2; ended || { echo "RUN-GONE e190 arm $ARM: no session process and no session end"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
grep -E 'session start|box and the build|config|sampler|stop-path|smoke|run [0-9]+-|STOP|no device opened|session end' "$L" 2>/dev/null | cut -c1-240 | tail -n 40
if ended; then
  echo "RUN-ENDED e190 arm $ARM"
  sleep 2
  if [ -s "$SD/MANIFEST.sha256" ]; then echo "MANIFEST-WRITTEN $(grep -c . "$SD/MANIFEST.sha256") files"; else echo "MANIFEST-ABSENT"; fi
else echo "RUN-RUNNING e190 arm $ARM after $t s"; fi
if grep -qE 'stop-path test failed|smoke gate failed|no device opened|the gate, no launch|would not start' "$L" 2>/dev/null; then echo "GATE-STOPPED e190 arm $ARM"; fi
EOF2
} > "$f"
rb_remote wait "$BOX" "one bounded wait on e190 arm $ARM" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on e190 arm $ARM exited $RB_RC"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "e190 arm $ARM is not running and recorded no end: read the box's logs (read-only) before anything else; the rest rule then counts it at its run's latest write"
rb_has '^MANIFEST-ABSENT' && rb_die $RB_E_FAIL "e190 arm $ARM has ended but its MANIFEST.sha256 is not written: wait once more, then read the box (read-only) before step 11"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "e190 arm $ARM ended at a gate (the lines above): step 11 still collects it"
rb_has '^RUN-ENDED' && { rb_say "e190 arm $ARM has ended ($(grep -m1 '^MANIFEST-WRITTEN' "$RB_CAP"))"; exit 0; }
rb_say "e190 arm $ARM still runs: call again"
exit $RB_E_AGAIN
