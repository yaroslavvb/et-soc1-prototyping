#!/usr/bin/env bash
# E184 (Q153), kit note 1 (../KIT.md.dated-note-1.md section 3), step 8: an arm's V3_DRY pass on its box, as one detached job of the runbook, no
# device opened: one pass, the smoke and the stop-path test through the arm's v2 block, and the v2 session's start gate refusing (exit 8) at
# a past E184_LATEST_START. The dry session writes only build/e184/session-<arm>-dry-t<T0>.log. The job is named <a3|a1c1>-dry-e184, which
# step 9 needs ended rc 0 today. V3_DRY keeps lib.sh's stub of the other-user test (no one present), so D1 itself is the desk's test.
# ../../e180/rb/s10_a3_dry_e180_v2.sh's form, for either box.
#
#   bash tools/claims-v3/e184/rb/s10_dry_e184.sh S|B start       then        ... S|B wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e184.sh"
rb_init s10_dry
e184_arm "${1:-}" || rb_die $RB_E_USAGE "usage: s10_dry_e184.sh S|B start|wait"
JOB=$E184_J-dry-e184
case "${2:-}" in
  start)
    rb_window
    body=$(rb_file body)
    { echo "LAST_END=$(printf '%q' "$RB_LAST_END"); ARM=$E184_ARM; CARD=$E184_CARD; SESS=$E184_SESS"
      cat <<'EOF2'
if [ "$ARM" = S ]; then BLK=tools/claims-v3/e184/block_e184s_v2.sh; P=18410; SM=18401; ST=18402; unset V3_DEVICE
else BLK=tools/claims-v3/e184/block_e184b_v2.sh; P=18442; SM=18431; ST=18432; export V3_DEVICE=1; fi
echo "== E184's V3_DRY blocks (kit v2), arm $ARM"
bad=0
V3_DRY=1 E184_DRY_BASES="16:30.40,24:33.10,32:35.60" bash $BLK $P; r=$?; echo "E184 dry $P rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash $BLK $SM --smoke; r=$?; echo "E184 dry $SM --smoke rc=$r"; [ "$r" -eq 0 ] || bad=1
V3_DRY=1 bash $BLK $ST --stoptest; r=$?; echo "E184 dry $ST --stoptest rc=$r"; [ "$r" -eq 0 ] || bad=1
echo "== E184's start gate at a past E184_LATEST_START (kit v2)"
V3_DRY=1 E184_T0=$(date +%s) E184_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E184_DEADLINE="$LAST_END" bash tools/claims-v3/e184/$SESS
g=$?; echo "E184 start gate rc=$g (want 8)"; [ "$g" -eq 8 ] || bad=1
rm -rf "build/claims-v3-dry/$CARD/e184" "build/claims-v3-dry/$CARD/e184-smoke" "build/claims-v3-dry/$CARD/e184-stoptest"
[ "$bad" -eq 0 ]
EOF2
    } > "$body"
    rb_probe "$E184_BOX"
    rb_job_start "$E184_BOX" "$JOB" "$body" 1
    ;;
  wait)
    rb_probe "$E184_BOX"
    rb_job_wait "$E184_BOX" "$JOB"; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'E184 dry 18410 rc=' 'E184 dry 18442 rc=' 'E184 dry 18401 --smoke rc=' 'E184 dry 18431 --smoke rc=' 'E184 dry 18402 --stoptest rc=' \
               'E184 dry 18432 --stoptest rc=' 'E184 start gate rc='; do grep -m1 "^$k" "$RB_CAP"; done
    fi
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s10_dry_e184.sh S|B start|wait" ;;
esac
