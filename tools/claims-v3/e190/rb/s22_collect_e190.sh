#!/usr/bin/env bash
# E190 (Q169, the kit), the box step "the copy-back" (this file is s22), for one arm: the arm's session directory copied back READ-ONLY from
# its box into RB_OUT/e190-raw/<arm>/T<T0>-<arm>/ and checked exact. E189's step 11's first half: the T0 the runbook launched
# (RB_OUT/e190-T0-<arm>.txt); the box read first (the session ended, its MANIFEST.sha256 written, no session_e190.sh of ours still running,
# the box's home path for the scrub, our own login there for the scrub check: RB_OUT/box-login-<box>.txt, which the look wrote); ONE
# bounded rsync from the box (a copy: nothing on the box is moved or removed); then collect_e190.py copy-check: COPY-BACK EXACT (every file
# of the box's manifest at its sha256, nothing else but runner.out and runner.rc). A session that stopped at a gate is copied the same way
# (E184's lesson). The data directory is step 12's (s23_data_e190.sh), once every arm that ran today is copied back.
#   bash tools/claims-v3/e190/rb/s22_collect_e190.sh <A|B>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e190.sh"
rb_init s22_collect
e190_arm "${1:-}"
e190_window
t0=; [ -f "$RB_OUT/e190-T0-$ARM.txt" ] && t0=$(cat "$RB_OUT/e190-T0-$ARM.txt")
[ -n "${RB_DRY:-}" ] && t0=${t0:-1794600000}
[ -n "$t0" ] || rb_die $RB_E_USAGE "RB_OUT holds no e190-T0-$ARM.txt: step 9 has not launched E190's arm $ARM from this RB_OUT"
rb_probe "$BOX"
f=$(rb_file ended)
{ rb_prelude "$BOX"
  echo "T0=$t0; ARM=$ARM"
  cat <<'EOF2'
SD=build/e190/T$T0-$ARM
[ -f "$SD/session.log" ] || { echo "REFUSED: no session directory $SD on $BOX"; exit 3; }
grep -q 'session end' "$SD/session.log" || { echo "REFUSED: $SD has no 'session end' yet: wait (step 10)"; exit 3; }
[ -s "$SD/MANIFEST.sha256" ] || { echo "REFUSED: $SD has no MANIFEST.sha256 yet: wait (step 10)"; exit 3; }
if [ "$(ours_live 'session_e190.sh')" -gt 0 ]; then echo "REFUSED: a session_e190.sh of ours still runs on $BOX"; exit 3; fi
echo "BOXHOME $HOME"
echo "FILES $(find "$SD" -type f | wc -l | tr -d ' ')"
EOF2
} > "$f"
rb_remote read "$BOX" "the session ended, its manifest written, nothing of ours running" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the copy exited $RB_RC: nothing copied"
bh=$(rb_val '^BOXHOME ([^ ]+)$')
case "$bh" in /*|DRY) ;; *) bh="" ;; esac
[ -n "${RB_DRY:-}" ] && bh=${bh:-/home/BOX}
[ -n "$bh" ] || rb_die $RB_E_FAIL "the box's home path did not come back: nothing copied"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_OUT/box-login-$BOX.txt" ] || rb_die $RB_E_USAGE "RB_OUT holds no box-login-$BOX.txt (k6's look writes it): run the look (s05_look_k6.sh $BOX) first"
echo "$bh" > "$RB_OUT/box-home-$ARM.txt"
mkdir -p "$RB_OUT/e190-raw/$ARM"
D="$RB_OUT/e190-raw/$ARM/T$t0-$ARM"
[ -n "${RB_DRY:-}" ] || [ ! -e "$D" ] || rb_die $RB_E_USAGE "$D exists already: never merge into an earlier copy (a new RB_OUT, or move it aside)"
rb_need_end 600
rb_probe "$BOX"
rb_local copy "$BOX" "the session directory, copied from the box (read-only there)" rsync -a -e "$RB_RSH" "$BOX:$(rb_tree "$BOX")/build/e190/T$t0-$ARM/" "$D/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy exited $RB_RC: run this step again (into a new RB_OUT/e190-raw/$ARM, after moving the partial one aside)"
rb_local desk local "COPY-BACK EXACT (collect_e190.py copy-check)" /usr/bin/python3 -B tools/claims-v3/e190/collect_e190.py copy-check "$D"
[ -n "${RB_DRY:-}" ] || rb_has '^COPY-BACK EXACT' || rb_die $RB_E_GATE "the copy is not exact (the lines above): commit nothing; copy again into a new RB_OUT/e190-raw/$ARM"
echo "$D" > "$RB_OUT/e190-copied-$ARM.txt"
rb_say "arm $ARM copied back exact: $D; once every arm that ran today is copied, step 12 (s23_data_e190.sh) makes the data directory"
