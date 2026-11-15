#!/usr/bin/env bash
# E191's kit, dated note 2 (Q184, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after
# E191's first session stopped at its smoke gate by a kit defect (1a4bc1e3), before any E191 pass datum; KIT.md.dated-note-2.md):
# step 11 v2: rb/s22_collect_e191.sh (unchanged beside it) for E191.md's dated amendment A1's second session: its data directory is
# docs/reports/data/<the window's day>-e191-blind-day-aifoundry1-c1-s2/ (the first session's, ...-c1/, is committed, 1a4bc1e3, and is never
# merged into), the session found by 'session_e191*.sh', and a session whose start line does not name "kit note 2" is refused (10): step
# 11 v2 collects session v2 only. Every other line is v1's. v1's header: E191, the box step "the release, then the
# collection" (this file is s22): after the card lane's release (when that day has a post), E191's session directory copied back
# READ-ONLY from aifoundry1 and turned into the data directory at the desk. E189's step 11 (tools/claims-v3/e189/rb/s22_collect_e189.sh,
# unchanged beside it) with E191's box and names: the T0 the runbook launched (RB_OUT/e191-T0.txt); the box read first (the session ended,
# its MANIFEST.sha256 written, no session_e191.sh of ours still running, by its own script; the box's home path for the scrub); ONE bounded
# rsync from the box into RB_OUT/e191-raw/T<T0>/ (a copy: nothing on the box is moved or removed); then collect_e191.py at the desk: COPY-BACK
# EXACT, the data directory docs/reports/data/<the window's day>-e191-blind-day-aifoundry1-c1/ in E191.md 8.1's form, each pass reduced by
# energy_reduce.py UNCHANGED, the scrub (the box home and our box login, which the look wrote to RB_OUT/box-login-aifoundry1.txt),
# SHA256SUMS and FILES.txt; then the desk-path gate (nopath_q142s.py) and the history check. A session that stopped at a gate is collected
# the same way. The scorer is NOT run here: commit the data directory first (through commit_lab.sh), then s24_score_e191.sh.
#   bash tools/claims-v3/e191/rb/s22_collect_e191.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e191.sh"
rb_init s22_collect_v2
e191_window
t0=; [ -f "$RB_OUT/e191-T0.txt" ] && t0=$(cat "$RB_OUT/e191-T0.txt")
[ -n "${RB_DRY:-}" ] && t0=${t0:-1794800000}
[ -n "$t0" ] || rb_die $RB_E_USAGE "RB_OUT holds no e191-T0.txt: step 9 has not launched E191 from this RB_OUT"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_OUT/box-login-aifoundry1.txt" ] || rb_die $RB_E_USAGE "RB_OUT holds no box-login-aifoundry1.txt (the look writes it): run s05_look_e191.sh first"
DATA=docs/reports/data/${RB_DAY:-DAY}-e191-blind-day-aifoundry1-c1-s2
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_REPO/$DATA" ] || rb_die $RB_E_USAGE "$DATA exists already: never merge into an earlier copy"
rb_probe aifoundry1
f=$(rb_file ended)
{ rb_prelude aifoundry1
  echo "T0=$t0"
  cat <<'EOF2'
SD=build/e191/T$T0
[ -f "$SD/session.log" ] || { echo "REFUSED: no session directory $SD on $BOX"; exit 3; }
grep -q 'session end' "$SD/session.log" || { echo "REFUSED: $SD has no 'session end' yet: wait (step 10)"; exit 3; }
[ -s "$SD/MANIFEST.sha256" ] || { echo "REFUSED: $SD has no MANIFEST.sha256 yet: wait (step 10)"; exit 3; }
if [ "$(ours_live 'session_e191*.sh')" -gt 0 ]; then echo "REFUSED: a session_e191*.sh of ours still runs"; exit 3; fi
grep -q 'plan FULL; kit note 2;' "$SD/session.log" || { echo "REFUSED: $SD is not a kit note 2 session (its start line does not name it): step 11 v2 collects the second session only"; exit 3; }
echo "BOXHOME $HOME"
echo "FILES $(find "$SD" -type f | wc -l | tr -d ' ')"
EOF2
} > "$f"
rb_remote read aifoundry1 "the session ended, its manifest written, nothing of ours running" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the copy exited $RB_RC: nothing copied"
bh=$(rb_val '^BOXHOME ([^ ]+)$')
case "$bh" in /*|DRY) ;; *) bh="" ;; esac
[ -n "${RB_DRY:-}" ] && bh=${bh:-/home/BOX}
[ -n "$bh" ] || rb_die $RB_E_FAIL "the box's home path did not come back: nothing copied"
mkdir -p "$RB_OUT/e191-raw"
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_OUT/e191-raw/T$t0" ] || rb_die $RB_E_USAGE "RB_OUT/e191-raw/T$t0 exists already: never merge into an earlier copy (a new RB_OUT, or move it aside)"
rb_need_end 600
rb_probe aifoundry1
rb_local copy aifoundry1 "the session directory, copied from the box (read-only there)" rsync -a -e "$RB_RSH" "aifoundry1:nekko/build/e191/T$t0/" "$RB_OUT/e191-raw/T$t0/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy exited $RB_RC: run this step again (into a new RB_OUT/e191-raw, after moving the partial one aside)"
rb_local desk local "COPY-BACK EXACT, the data directory, the reducer (unchanged), the scrub, SHA256SUMS and FILES.txt (collect_e191.py)" \
  /usr/bin/python3 -B tools/claims-v3/e191/collect_e191.py "$RB_OUT/e191-raw/T$t0" "$DATA" --box-home "$bh" --box-login "$RB_OUT/box-login-aifoundry1.txt"
[ -n "${RB_DRY:-}" ] || rb_has '^COLLECTED ' || rb_die $RB_E_GATE "the collection did not read COLLECTED (the lines above): commit nothing"
rb_nopath "$RB_REPO/$DATA"
rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e191/rb/check_history_e191.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed after the collection"
rb_say "collected $DATA: write its README (FILES.txt lists every file for its Files table), commit it through commit_lab.sh (new files only), then run s24_score_e191_v2.sh on the committed data"
