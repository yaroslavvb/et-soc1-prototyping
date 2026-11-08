#!/usr/bin/env bash
# E183 (Q155, the kit), KIT.md box step 8: a V3_DRY pass on the box as one detached job (E180's step 8 v2, ported): train block 18310 with
# all its processes, the smoke and the stop-path test, each under V3_DRY (no device opens), then the session's start gate at a past
# E183_LATEST_START (it must refuse, 8, with no device opened). Refused beside a session of ours (k6's rb_job_start).
#   bash tools/claims-v3/e183/rb/s10_a3_dry_e183.sh start      then      ... wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e183.sh"
rb_init s10_a3_dry
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
V3_DRY=1 bash tools/claims-v3/e183/block_e183.sh 18310; r=$?; echo "E183 dry 18310 rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e183/block_e183.sh 18301 --smoke; r=$?; echo "E183 dry 18301 --smoke rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash tools/claims-v3/e183/block_e183.sh 18302 --stoptest; r=$?; echo "E183 dry 18302 --stoptest rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E183's start gate at a past E183_LATEST_START"
V3_DRY=1 E183_T0=$(date +%s) E183_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E183_DEADLINE="$LAST_END" bash tools/claims-v3/e183/session_e183.sh
g=$?; echo "E183 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
rm -rf build/claims-v3-dry/aifoundry3/e183 build/claims-v3-dry/aifoundry3/e183-smoke build/claims-v3-dry/aifoundry3/e183-stoptest
[ "$bad" -eq 0 ]
EOF2
    } > "$body"
    rb_probe aifoundry3
    rb_job_start aifoundry3 a3-dry-e183 "$body" 1
    ;;
  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 a3-dry-e183; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'E183 dry 18310 rc=' 'E183 dry 18301 --smoke rc=' 'E183 dry 18302 --stoptest rc=' 'E183 start gate rc='; do
        grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"
      done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e183.sh start|wait" ;;
esac
