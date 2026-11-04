#!/usr/bin/env bash
# Q141(k), go checklist step 1 (his: approve the Tailscale checks). The session probes each box first and hands him every link it
# prints. Each probe is `ssh -o BatchMode=yes -o ConnectTimeout=10 <box> true`, hard-killed at 15 s; a printed link appends
# "<HH:MM:SS> <box> needs a check" to $RB_LOCK and is kept in $RB_OUT/links.txt (never in the repo) for him.
#
#   RB_OUT=<day dir> RB_LOCK=<tailscale-needed file> bash tools/claims-v3/q141k-runbook/s01_probe.sh [aifoundry1 aifoundry2 aifoundry3]
#
# Exit 0 every box answered; 11 at least one printed a link (approve each, then probe again); 12 one did not answer (no link).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s01_probe
boxes=${*:-aifoundry1 aifoundry2 aifoundry3}
worst=0
for b in $boxes; do
  rb_tree "$b" > /dev/null || rb_die $RB_E_USAGE "unknown box: $b"
  if [ -n "${RB_DRY:-}" ]; then rb_probe "$b"; continue; fi
  "$RB_PY" -B "$RB_DIR/rb_run.py" --cls probe --host "$b" --step "$RB_STEP" --what probe -- ssh $RB_SSHO "$b" true
  rc=$?
  case $rc in
    0) rb_say "$b answers" ;;
    11) rb_say "$b needs a check: the link is in $RB_LINKS"; worst=11 ;;
    *) rb_say "$b did not answer within 15 s (rc $rc)"; [ "$worst" -eq 0 ] && worst=12 ;;
  esac
done
[ "$worst" -eq 11 ] && { echo "links to approve (one per box):"; tail -n 6 "$RB_LINKS" 2>/dev/null; }
exit "$worst"
