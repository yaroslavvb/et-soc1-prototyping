#!/usr/bin/env bash
# E186 kit note 1 (Q158, fix-e186), KIT.md box step 5 v2 (this file is s07 v2): the sync, never beside a card session of ours and never under
# a runbook job (verify-e186's fault 3). Step 5 v1 (rb/s07_a3_sync_e186.sh) rsyncs into ~/aifoundry with no read of the box first, so with a
# session of ours live (day 2's E183 or E185, or E186's own) it synced into the tree that session runs from and loaded the host during its
# measurement (the verifier's case HS: rc 0, one rsync call). v2 first makes ONE bounded read on the box, k6's prelude and its two counts
# (ours_live: any session_eNNN.sh or queue_eNNN.sh of ours; jobs_live: a runbook job of any day still running, step 6's build among them),
# and refuses (10) if either is above 0; only then it runs step 5 v1, UNCHANGED (its window, its last start, its sync list, its clean
# paths, HARNESS OK 71, NOTE1 FILES OK 10, its probe, its one itemized rsync). The read sends no device command (pgrep and /proc only).
#
#   bash tools/claims-v3/e186/rb/s07_a3_sync_e186_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e186.sh"
rb_init s07_a3_sync_v2
e186_window
rb_need_start
rb_probe aifoundry3
f=$(rb_file notours)
{ rb_prelude aifoundry3
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E186's step 5 never syncs beside one (kit note 1; one session of ours at a time)"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E186's step 5 never syncs under one (kit note 1; read them with their own step first)"; exit 3; fi
echo "NOT-BESIDE-OURS: no card session of ours and no runbook job on $BOX"
EOF2
} > "$f"
rb_remote read aifoundry3 "no card session of ours and no runbook job on the box before the sync (k6's ours_live and jobs_live)" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the sync exited $RB_RC: nothing synced"
[ -n "${RB_DRY:-}" ] || rb_has '^NOT-BESIDE-OURS: ' || rb_die $RB_E_FAIL "the read before the sync gave no answer: nothing synced"
rb_say "no card session of ours and no runbook job on aifoundry3: step 5 v1 next, unchanged"
bash "$RB_E186_DIR/s07_a3_sync_e186.sh"
r=$?
[ "$r" -eq 0 ] || { echo "[$RB_STEP] step 5 v1 exited $r (its lines above)"; echo "$(date '+%F %T %Z') step=$RB_STEP exit=$r step 5 v1 exited $r" >> "$RB_LOG"; exit "$r"; }
exit 0
