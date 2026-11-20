#!/usr/bin/env bash
# E220 (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum), the box step "the dry pass" (this file is s10; step 8): E215 arm A's step 8
# (tools/claims-v3/e215/rb/s10_dry_e215.sh, landed in 8bde0182, run on aifoundry3 today) for E220: start runs run_e220a.py --dry on the box as a
# detached runbook job (the doubles, fake_card_e220a.py: no device, no lock), the short sequence (the opening smoke s01, the stop-path test and the
# first three runs: t01, y06b, y08a); wait reads its verdict (E220-DRY arm A rc=0 runs=3, the smoke gate passed, the stop-path test passed, the
# identity read, the manifest) and THEN THE SCRUB CHECK BEFORE THE SESSION (E209's lesson: its collection's scrub refused a real record after its
# session and the day was spent): the box's home in every form ($HOME, the user database's home, the home's physical path: RB_OUT/box-home-A.txt,
# which step 11 writes again), the dry pass's folder copied back read-only, and collect_e220a.py scrub-check on it (a private copy scrubbed by the
# collection's own code, nothing written in the lab): SCRUB-CHECK CLEAN, else 16 and no session that day.
#   bash tools/claims-v3/e220/rb/s10_dry_e220a.sh A start | wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e220a.sh"
rb_init s10_dry
e220a_arm "${1:-}"
act=${2:-}
e220a_jobs "$ARM"
JOB=$JOB_DRY
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_dry_e220a.sh A start | wait" ;; esac
e220a_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe "$BOX"
  body=$(rb_file body)
  { echo "ARM=$ARM"
    cat <<'EOF2'
T0=$(date +%s)
D=build/e220a/T$T0-$ARM-dry
E220A_FAKE_SCALE=0.05 E220A_FAKE_TAU_S=1 python3 -B tools/claims-v3/e220/run_e220a.py session --dry --arm "$ARM" --t0 "$T0" --out "$D" \
  --sequence short --rest-s 1 --smoke-rest-s 3 --tail-s 0.5 --gate-wait-s 20
rc=$?
echo "E220-DRY-DIR $D"
grep -E 'identity|stop-path|smoke gate|run [0-9]+-.* done|STOP|HUNG|session end' "$D/session.log" | cut -c1-200
n=$(grep -c 'run [0-9]*-.* done: .* rc \[0\]' "$D/session.log")
echo "E220-DRY arm $ARM rc=$rc runs=$n"
[ "$rc" -eq 0 ] && [ "$n" -ge 3 ] && grep -q 'smoke gate passed' "$D/session.log" && grep -q 'stop-path test passed' "$D/session.log" && \
  grep -q 'the identity read: ' "$D/session.log" && [ -s "$D/MANIFEST.sha256" ]
EOF2
  } > "$body"
  rb_job_start "$BOX" "$JOB" "$body"
  rb_say "the dry pass $JOB started on $BOX: run this step's wait (bounded) until it ends"
  exit 0
fi
rb_probe "$BOX"
rb_job_wait "$BOX" "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && exit 0
[ "$rc" -eq 0 ] || exit "$rc"
dd=$(sed -nE 's#^E220-DRY-DIR (build/e220a/T[0-9]+-A-dry)$#\1#p' "$RB_CAP" 2>/dev/null | head -n 1)   # '#': rb_val's sed would read the path's '/' as its delimiter
[ -n "$dd" ] || rb_die $RB_E_FAIL "the dry pass named no folder (E220-DRY-DIR): run the dry pass again"
rb_say "the dry pass ended rc 0: $(grep -m1 '^E220-DRY arm' "$RB_CAP")"
# THE SCRUB CHECK BEFORE THE SESSION (E209's lesson): the dry pass's own folder, written on the box with the box's paths in its argv, logs and
# records, copied back read-only and scrubbed on a private copy at the desk by the collection's own code; a file the scrub cannot clean stops the
# day HERE (16), before any card time, not after the session
rb_probe "$BOX"
f=$(rb_file homes)
{ rb_prelude "$BOX"; e220a_homes_text; } > "$f"
rb_remote read "$BOX" "the box's home in every form the scrub masks" "$f"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the homes read exited $RB_RC: run this step's wait again"
grep -E '^BOXHOME /' "$RB_CAP" | sed 's/^BOXHOME //' | awk '!seen[$0]++' > "$RB_OUT/box-home-$ARM.txt"
[ -s "$RB_OUT/box-home-$ARM.txt" ] || rb_die $RB_E_FAIL "the box's home did not come back"
[ -s "$RB_OUT/box-login-$BOX.txt" ] || rb_die $RB_E_USAGE "RB_OUT holds no box-login-$BOX.txt (k6's look writes it): run the look first"
C="$RB_OUT/e220a-dry-copy-$ARM-$(date +%H%M%S)"
rb_probe "$BOX"
rb_local copy "$BOX" "the dry pass's folder, copied from the box (read-only there)" rsync -a -e "$RB_RSH" "$BOX:$(rb_tree "$BOX")/$dd/" "$C/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the dry pass's copy exited $RB_RC: run this step's wait again"
rb_local desk local "THE SCRUB CHECK on the dry pass's copy (collect_e220a.py scrub-check: a private copy scrubbed, nothing written in the lab)" \
  /usr/bin/python3 -B tools/claims-v3/e220/collect_e220a.py scrub-check "$C" "$RB_OUT/box-home-$ARM.txt" "$RB_OUT/box-login-$BOX.txt"
rb_has '^SCRUB-CHECK CLEAN: ' || rb_die $RB_E_GATE "the scrub check on the dry pass's records did not read CLEAN (the lines above): the collection would refuse this box's records after the session: no session today; a kit note first"
rb_say "the scrub check on the dry pass's copy: $(grep -m1 '^SCRUB-CHECK CLEAN: ' "$RB_CAP")"
exit 0
