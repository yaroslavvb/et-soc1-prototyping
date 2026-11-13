#!/usr/bin/env bash
# E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): KIT.md box step 8 v3, the V3_DRY
# pass on the box. It is rb/s10_a3_dry_e183_v2.sh (24b9b99e, which stays as committed) with two changes, each marked "note 6": its job runs
# block_e183_v3.sh and the start gate of session_e183_v3.sh, and its job is named a3-dry-e183-v3, so step 9 v3 reads a dry pass of note 6's
# files made today and never the morning's a3-dry-e183 (block v2's, Fri 13 Nov 2026's first session). What it runs and every reading are
# v2's. A dry pass cannot see the post-block check (V3_DRY skips it, the lesson of that session): the real-path desk test
# (desk/desktest_realpath_e183.sh) runs it at the desk. Its name in the runbook's log is s10_a3_dry_v3_e183.
#   bash tools/claims-v3/e183/rb/s10_a3_dry_e183_v3.sh start      then      ... wait   (repeat while it says 17)
# v2's words follow:
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): KIT.md box step 8 v2, the V3_DRY pass on
# the box. It is rb/s10_a3_dry_e183.sh (cc597bf2, which stays as committed) with one change: its job runs block_e183_v2.sh and the start gate
# of session_e183_v2.sh (v1's block greps the train host for 'train_kind' in its preflight, even under V3_DRY, so with a host built by GCC
# at -O2 v1's dry pass would refuse every block). Its job name (a3-dry-e183), what it runs and every reading are v1's, so step 9 v2's
# "today's dry pass" reads it unchanged; its name in the runbook's log is s10_a3_dry_v2_e183.
#   bash tools/claims-v3/e183/rb/s10_a3_dry_e183_v2.sh start      then      ... wait   (repeat while it says 17)
# v1's words follow:
# E183 (Q155, the kit), KIT.md box step 8: a V3_DRY pass on the box as one detached job (E180's step 8 v2, ported): train block 18310 with
# all its processes, the smoke and the stop-path test, each under V3_DRY (no device opens), then the session's start gate at a past
# E183_LATEST_START (it must refuse, 8, with no device opened). Refused beside a session of ours (k6's rb_job_start).
#   bash tools/claims-v3/e183/rb/s10_a3_dry_e183.sh start      then      ... wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e183.sh"
rb_init s10_a3_dry_v3
act=${1:-}
case "$act" in
  start)
    rb_window
    body=$(rb_file body)
    { echo "LAST_START=$(printf '%q' "$RB_LAST_START")"
      echo "LAST_END=$(printf '%q' "$RB_LAST_END")"
      cat <<'EOF2'
echo "== E183's V3_DRY blocks"
bad=0
V3_DRY=1 bash tools/claims-v3/e183/block_e183_v3.sh 18310; r=$?; echo "E183 dry 18310 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e183/block_e183_v3.sh 18301 --smoke; r=$?; echo "E183 dry 18301 --smoke rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e183/block_e183_v3.sh 18302 --stoptest; r=$?; echo "E183 dry 18302 --stoptest rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E183's start gate at a past E183_LATEST_START"
V3_DRY=1 E183_T0=$(date +%s) E183_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E183_DEADLINE="$LAST_END" bash tools/claims-v3/e183/session_e183_v3.sh
g=$?; echo "E183 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
rm -rf build/claims-v3-dry/aifoundry3/e183 build/claims-v3-dry/aifoundry3/e183-smoke build/claims-v3-dry/aifoundry3/e183-stoptest
[ "$bad" -eq 0 ]
EOF2
    } > "$body"
    rb_probe aifoundry3
    rb_job_start aifoundry3 a3-dry-e183-v3 "$body" 1     # note 6: its own job name
    ;;
  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 a3-dry-e183-v3; rc=$?     # note 6
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'E183 dry 18310 rc=' 'E183 dry 18301 --smoke rc=' 'E183 dry 18302 --stoptest rc=' 'E183 start gate rc='; do
        grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"
      done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e183_v3.sh start|wait" ;;
esac
