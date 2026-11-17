#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum), the box step "the copy-back" (this file is s22; step 11), for one arm:
# E190's step 11 v2 (rb/s22_collect_e190_v2.sh) counting E206's session by ITS name, session_e206.sh, before the copy (none of ours still
# running). The T0 the runbook launched (RB_OUT/e206-T0-<arm>.txt); the box read first (the session ended, its MANIFEST.sha256 written, the
# box's home path and our own login there for the scrub); ONE bounded rsync from the box (a copy: nothing on the box is moved or removed);
# then collect_e206.py copy-check: COPY-BACK EXACT. A session that stopped at a gate is copied the same way. A HUNG session: its hung
# process may still write its own .out and .err after the manifest, so the copy may not read exact: commit nothing then, and collect it by
# a dated note's decision (CARD-LANE-BRIEF.md 3). The data directory is step 12's (s23_data_e206.sh). The card lane runs
# `bash W/onelab.sh collect <lane>` right before this step (THE ONE-LAB RULE).
#   bash tools/claims-v3/e206/rb/s22_collect_e206.sh <A|B>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e206.sh"
rb_init s22_collect
e206_arm "${1:-}"
e206_window
t0=; [ -f "$RB_OUT/e206-T0-$ARM.txt" ] && t0=$(cat "$RB_OUT/e206-T0-$ARM.txt")
[ -n "${RB_DRY:-}" ] && t0=${t0:-1794800000}
[ -n "$t0" ] || rb_die $RB_E_USAGE "RB_OUT holds no e206-T0-$ARM.txt: step 9 has not launched E206's arm $ARM from this RB_OUT"
rb_probe "$BOX"
f=$(rb_file ended)
{ rb_prelude "$BOX"
  echo "T0=$t0; ARM=$ARM"
  cat <<'EOF2'
SD=build/e206/T$T0-$ARM
[ -f "$SD/session.log" ] || { echo "REFUSED: no session directory $SD on $BOX"; exit 3; }
grep -q 'session end' "$SD/session.log" || { echo "REFUSED: $SD has no 'session end' yet: wait (step 10)"; exit 3; }
[ -s "$SD/MANIFEST.sha256" ] || { echo "REFUSED: $SD has no MANIFEST.sha256 yet: wait (step 10)"; exit 3; }
if [ "$(ours_live 'session_e206*.sh')" -gt 0 ]; then echo "REFUSED: a session_e206.sh of ours still runs on $BOX"; exit 3; fi
echo "BOXHOME $HOME"
echo "FILES $(find "$SD" -type f | wc -l | tr -d ' ')"
EOF2
} > "$f"
rb_remote read "$BOX" "the session ended, its manifest written, no session of ours running" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the copy exited $RB_RC: nothing copied"
bh=$(rb_val '^BOXHOME ([^ ]+)$')
case "$bh" in /*|DRY) ;; *) bh="" ;; esac
[ -n "${RB_DRY:-}" ] && bh=${bh:-/home/BOX}
[ -n "$bh" ] || rb_die $RB_E_FAIL "the box's home path did not come back: nothing copied"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_OUT/box-login-$BOX.txt" ] || rb_die $RB_E_USAGE "RB_OUT holds no box-login-$BOX.txt (k6's look writes it): run the look (s05_look_k6.sh $BOX) first"
echo "$bh" > "$RB_OUT/box-home-$ARM.txt"
mkdir -p "$RB_OUT/e206-raw/$ARM"
D="$RB_OUT/e206-raw/$ARM/T$t0-$ARM"
[ -n "${RB_DRY:-}" ] || [ ! -e "$D" ] || rb_die $RB_E_USAGE "$D exists already: never merge into an earlier copy (a new RB_OUT, or move it aside)"
rb_need_end 600
rb_probe "$BOX"
rb_local copy "$BOX" "the session directory, copied from the box (read-only there)" rsync -a -e "$RB_RSH" "$BOX:$(rb_tree "$BOX")/build/e206/T$t0-$ARM/" "$D/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy exited $RB_RC: run this step again (into a new RB_OUT/e206-raw/$ARM, after moving the partial one aside)"
rb_local desk local "COPY-BACK EXACT (collect_e206.py copy-check)" /usr/bin/python3 -B tools/claims-v3/e206/collect_e206.py copy-check "$D"
[ -n "${RB_DRY:-}" ] || rb_has '^COPY-BACK EXACT' || rb_die $RB_E_GATE "the copy is not exact (the lines above): commit nothing; copy again into a new RB_OUT/e206-raw/$ARM"
echo "$D" > "$RB_OUT/e206-copied-$ARM.txt"
rb_say "arm $ARM copied back exact: $D; step 12 (s23_data_e206.sh $ARM) makes the data directory"
