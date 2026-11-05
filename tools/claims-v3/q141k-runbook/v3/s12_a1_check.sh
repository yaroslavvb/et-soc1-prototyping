#!/usr/bin/env bash
# Q141(k), go checklist step 12: aifoundry1 card 1, the kit's own box steps 2 and 3 (E164 README; README.md.dated-note.md § 5):
#   sync: bash tools/claims-v3/e164/box/sync_e164.sh, run on the Intel (two rsyncs into ~/nekko: e164/ without dry/, and pool 7);
#   check: tools/claims-v3/e164/box/check_box_e164.sh on the box (check_e164.py HARNESS OK with the binaries 4f0956ce / e0fbecce /
#   990807f4 / 8008f96f, preflight GO, the tiles, pool 7's 91, the V3_DRY pass 16410, smoke 16401 and stop-path test 16402, et-who).
# The check takes about 4 minutes, so it runs detached on the box as a dry job (the same script, from ~/nekko, where sync_e164.sh put
# it), and is waited on with bounded calls. The host's identity (uptime -s before 31 Oct 13:45:24 PDT) is look_e164.sh's (step 5).
#
#   bash tools/claims-v3/q141k-runbook/v2/s12_a1_check.sh sync     # a copy, 600 s
#   bash tools/claims-v3/q141k-runbook/v2/s12_a1_check.sh start    # starts the check, detached: returns at once
#   bash tools/claims-v3/q141k-runbook/v2/s12_a1_check.sh wait     # one bounded wait; 17 = call again
# v2 (Q141(k)'s verifier, faults 1 and 2): a clean wait writes RB_OUT/a1-check-clean.txt (the window's day, "clean"), which s13
# needs before it launches E164, and start removes it; a lost check job (no process, no exit status) exits 14 with JOB-LOST, and a
# job not started today exits 10.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s12_a1_check
rb_window
case "${1:-}" in
  sync)
    rb_probe aifoundry1
    rb_local copy aifoundry1 "box/sync_e164.sh (E164 box step 2)" bash tools/claims-v3/e164/box/sync_e164.sh
    [ "$RB_RC" -eq 0 ] && rb_has '^synced: ' || rb_die $RB_E_FAIL "sync_e164.sh did not finish (rc $RB_RC)"
    rb_say "aifoundry1: synced tools/claims-v3/e164/ and pool 7 into ~/nekko"
    ;;
  start)
    [ -n "${RB_DRY:-}" ] || rm -f "$RB_OUT/a1-check-clean.txt"
    body=$(rb_file body)
    cat > "$body" <<'EOF'
bash tools/claims-v3/e164/box/check_box_e164.sh
EOF
    rb_probe aifoundry1
    rb_job_start aifoundry1 a1-check "$body" 1
    ;;
  wait)
    rb_probe aifoundry1
    rb_job_wait aifoundry1 a1-check; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    [ "$rc" -eq "$RB_E_AGAIN" ] && exit "$rc"
    [ "$rc" -eq "$RB_E_USAGE" ] && exit "$rc"            # not started today: s12_a1_check.sh start first
    rb_has '^JOB-LOST' && exit "$RB_E_FAIL"              # lost: start it again (the wait said why)
    bad=""
    # check_box_e164.sh's own lines, section by section (each "== <name>" header, then its first "rc=" line)
    sec() { awk -v want="$1" '/^== /{s=substr($0, 4); next} /^rc=/{ if (s == want && !done) {print; done=1} }' "$RB_CAP"; }
    rb_has '^HARNESS OK' || bad="$bad harness"
    sec 'check_e164 (with the binaries)' | grep -qx 'rc=0' || bad="$bad check_e164"
    sec 'preflight' | grep -q '^rc=0 ' || bad="$bad preflight"
    sec 'tiles' | grep -qx 'rc=0' || bad="$bad tiles"
    grep -A1 "^== pool 7's SHA256SUMS" "$RB_CAP" | grep -qx '91' || bad="$bad blind7"
    sec 'dry pass 16410' | grep -qE '^rc=0 \(want 0\) [1-9][0-9]* device calls printed' || bad="$bad dry-pass"
    sec 'dry smoke 16401' | grep -q '^rc=0 (want 0)' || bad="$bad dry-smoke"
    sec 'dry stop-path test 16402' | grep -q '^rc=1 ' || bad="$bad dry-stoptest"
    [ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry1's box check did not read clean:$bad (read the output above; a binary that differs needs a dated amendment)"
    echo "$RB_DAY clean $(date '+%F %T %Z')" > "$RB_OUT/a1-check-clean.txt"     # s13 launches only after this (step 12 before 13)
    rb_say "aifoundry1 card 1: harness OK, preflight GO, tiles OK, blind7 91, dry pass rc 0, smoke rc 0, stop-path test rc 1 (as a dry run ends)"
    ;;
  *) rb_die $RB_E_USAGE "usage: s12_a1_check.sh sync|start|wait" ;;
esac
