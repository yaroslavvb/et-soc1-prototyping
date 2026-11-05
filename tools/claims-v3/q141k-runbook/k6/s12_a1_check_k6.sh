#!/usr/bin/env bash
# Q142(k6), step 12: aifoundry1 card 1 for E172 (E172's README, box steps 2-3): sync (box/sync_e172.sh, on the Intel), then the box
# check as one detached job (box/check_box_e172.sh: the harness with the binaries, the preflight, the tiles, pool 8's SHA256SUMS, the
# dry pass, the dry smoke and the dry stop-path test), then one bounded wait that reads each section and writes the day's
# a1-check-clean-e172.txt, which s13 needs. A port of ../v3.1/s12_a1_check.sh.
#
#   bash tools/claims-v3/q141k-runbook/k6/s12_a1_check_k6.sh sync | start | wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s12_a1_check
rb_window
case "${1:-}" in
  sync)
    rb_probe aifoundry1
    rb_local copy aifoundry1 "box/sync_e172.sh (E172 box step 2)" bash tools/claims-v3/e172/box/sync_e172.sh
    [ "$RB_RC" -eq 0 ] && rb_has '^synced: ' || rb_die $RB_E_FAIL "sync_e172.sh did not finish (rc $RB_RC)"
    rb_say "aifoundry1: synced tools/claims-v3/e172/, pool 8 and the pinned watcher files into ~/nekko"
    ;;
  start)
    [ -n "${RB_DRY:-}" ] || rm -f "$RB_OUT/a1-check-clean-e172.txt"
    body=$(rb_file body)
    cat > "$body" <<'EOF'
bash tools/claims-v3/e172/box/check_box_e172.sh
EOF
    rb_probe aifoundry1
    rb_job_start aifoundry1 a1-check-e172 "$body" 1
    ;;
  wait)
    rb_probe aifoundry1
    rb_job_wait aifoundry1 a1-check-e172; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    [ "$rc" -eq "$RB_E_AGAIN" ] && exit "$rc"
    [ "$rc" -eq "$RB_E_USAGE" ] && exit "$rc"            # not started today: s12_a1_check.sh start first
    rb_has '^JOB-LOST' && exit "$RB_E_FAIL"              # lost: start it again (the wait said why)
    bad=""
    # check_box_e172.sh's own lines, section by section (each "== <name>" header, then its first "rc=" line)
    sec() { awk -v want="$1" '/^== /{s=substr($0, 4); next} /^rc=/{ if (s == want && !done) {print; done=1} }' "$RB_CAP"; }
    rb_has '^HARNESS OK' || bad="$bad harness"
    sec 'check_e172 (with the binaries)' | grep -qx 'rc=0' || bad="$bad check_e172"
    sec 'preflight' | grep -q '^rc=0 ' || bad="$bad preflight"
    sec 'tiles' | grep -qx 'rc=0' || bad="$bad tiles"
    grep -A1 "^== pool 8's SHA256SUMS" "$RB_CAP" | grep -qx '89' || bad="$bad blind8"
    sec 'dry pass 17210' | grep -qE '^rc=0 \(want 0\) [1-9][0-9]* device calls printed' || bad="$bad dry-pass"
    sec 'dry smoke 17201' | grep -q '^rc=0 (want 0)' || bad="$bad dry-smoke"
    sec 'dry stop-path test 17202' | grep -q '^rc=1 ' || bad="$bad dry-stoptest"
    [ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry1's box check did not read clean:$bad (read the output above; a binary that differs needs a dated amendment)"
    echo "$RB_DAY clean $(date '+%F %T %Z')" > "$RB_OUT/a1-check-clean-e172.txt"     # s13 launches only after this (step 12 before 13)
    rb_say "aifoundry1 card 1 (E172): harness OK, preflight GO, tiles OK, blind8 89, dry pass rc 0, smoke rc 0, stop-path test rc 1 (as a dry run ends)"
    ;;
  *) rb_die $RB_E_USAGE "usage: s12_a1_check_k6.sh sync|start|wait" ;;
esac
