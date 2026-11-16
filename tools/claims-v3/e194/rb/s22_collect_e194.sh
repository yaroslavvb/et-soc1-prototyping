#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum), the box step "the collection" (this
# file is s22): E194's session directory copied back READ-ONLY from aifoundry2's box tree (this same machine, reached as k6 reaches it) and
# turned into the data directory at the desk. E191's step 11 (tools/claims-v3/e191/rb/s22_collect_e191.sh, unchanged beside it) with E194's
# box and names: THE QUIET DESK FLAG still raised (it is lowered after this step's COPY-BACK EXACT, by rb/quiet_e194.sh lower); the T0 the
# runbook launched (RB_OUT/e194-T0.txt); the box read first (the session ended, its MANIFEST.sha256 written, no session_e194.sh of ours
# still running, by its own script; the box's home path for the scrub); ONE bounded rsync from aifoundry2:claude/et-soc1-prototyping/
# build/e194/T<T0>/ into RB_OUT/e194-raw/T<T0>/ (a copy: nothing in the box tree is moved or removed); then collect_e194.py at the desk:
# COPY-BACK EXACT, THE BOX-TREE GATE (every path under this account's home in the session's files lies in the box tree; no session scratch
# root: on this box a desk path carries the same home, so this gate runs before the scrub can hide it), the data directory
# docs/reports/data/<the window's day>-e194-blind-day-aifoundry2/ in E194.md 8.1's form, each pass reduced by energy_reduce.py UNCHANGED,
# the scrub (the box home and our box login, which the look wrote to RB_OUT/box-login-aifoundry2.txt), SHA256SUMS and FILES.txt; then k6's
# desk-path gate (nopath_q142s.py) and the history check. A session that stopped at a gate is collected the same way. The scorer is NOT
# run here: commit the data directory first (through commit_lab.sh), then s24_score_e194.sh. fix-e194 (verify-e194's finding 3): the box read
# before the copy prints the runner's exit status (runner.rc, written by session_e194.sh after the runner exits), and this step reports it
# in its last line; the data README names it (rb/data-readme-form-e194.md section 2).
#   RB_QUIET=<the flag file> bash tools/claims-v3/e194/rb/s22_collect_e194.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e194.sh"
rb_init s22_collect
e194_window
e194_quiet
t0=; [ -f "$RB_OUT/e194-T0.txt" ] && t0=$(cat "$RB_OUT/e194-T0.txt")
[ -n "${RB_DRY:-}" ] && t0=${t0:-1794800000}
[ -n "$t0" ] || rb_die $RB_E_USAGE "RB_OUT holds no e194-T0.txt: step 9 has not launched E194 from this RB_OUT"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_OUT/box-login-aifoundry2.txt" ] || rb_die $RB_E_USAGE "RB_OUT holds no box-login-aifoundry2.txt (the look writes it): run s05_look_e194.sh first"
DATA=docs/reports/data/${RB_DAY:-DAY}-e194-blind-day-aifoundry2
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_REPO/$DATA" ] || rb_die $RB_E_USAGE "$DATA exists already: never merge into an earlier copy"
rb_probe aifoundry2
f=$(rb_file ended)
{ rb_prelude aifoundry2
  echo "T0=$t0"
  cat <<'EOF2'
SD=build/e194/T$T0
[ -f "$SD/session.log" ] || { echo "REFUSED: no session directory $SD on $BOX"; exit 3; }
grep -q 'session end' "$SD/session.log" || { echo "REFUSED: $SD has no 'session end' yet: wait (step 10)"; exit 3; }
[ -s "$SD/MANIFEST.sha256" ] || { echo "REFUSED: $SD has no MANIFEST.sha256 yet: wait (step 10)"; exit 3; }
if [ "$(ours_live session_e194.sh)" -gt 0 ]; then echo "REFUSED: session_e194.sh still runs"; exit 3; fi
echo "BOXHOME $HOME"
echo "FILES $(find "$SD" -type f | wc -l | tr -d ' ')"
if [ -s "$SD/runner.rc" ]; then echo "RUNNERRC $(tr -dc '0-9' < "$SD/runner.rc")"; else echo "RUNNERRC none"; fi
EOF2
} > "$f"
rb_remote read aifoundry2 "the session ended, its manifest written, nothing of ours running" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the copy exited $RB_RC: nothing copied"
bh=$(rb_val '^BOXHOME ([^ ]+)$')
rrc=$(rb_val '^RUNNERRC ([0-9]+|none)$')                         # fix-e194 (finding 3): reported, never a gate here
case "$bh" in /*|DRY) ;; *) bh="" ;; esac
[ -n "${RB_DRY:-}" ] && bh=${bh:-/home/BOX}
[ -n "$bh" ] || rb_die $RB_E_FAIL "the box's home path did not come back: nothing copied"
mkdir -p "$RB_OUT/e194-raw"
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_OUT/e194-raw/T$t0" ] || rb_die $RB_E_USAGE "RB_OUT/e194-raw/T$t0 exists already: never merge into an earlier copy (a new RB_OUT, or move it aside)"
rb_need_end 600
rb_probe aifoundry2
rb_local copy aifoundry2 "the session directory, copied from the box (read-only there)" rsync -a -e "$RB_RSH" "aifoundry2:claude/et-soc1-prototyping/build/e194/T$t0/" "$RB_OUT/e194-raw/T$t0/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy exited $RB_RC: run this step again (into a new RB_OUT/e194-raw, after moving the partial one aside)"
rb_local desk local "COPY-BACK EXACT, THE BOX-TREE GATE, the data directory, the reducer (unchanged), the scrub, SHA256SUMS and FILES.txt (collect_e194.py)" \
  /usr/bin/python3 -B tools/claims-v3/e194/collect_e194.py "$RB_OUT/e194-raw/T$t0" "$DATA" --box-home "$bh" --box-login "$RB_OUT/box-login-aifoundry2.txt"
[ -n "${RB_DRY:-}" ] || rb_has '^COLLECTED ' || rb_die $RB_E_GATE "the collection did not read COLLECTED (the lines above): commit nothing"
rb_nopath "$RB_REPO/$DATA"
rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e194/rb/check_history_e194.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed after the collection"
rb_say "collected $DATA (the runner exited ${rrc:-unread}: 0 at an ordinary end, 16 at a gate, anything else a runner fault the README names; COPY-BACK EXACT: lower THE QUIET DESK FLAG now, rb/quiet_e194.sh lower <lane>): write its README (FILES.txt lists every file for its Files table), commit it through commit_lab.sh (new files only), then run s24_score_e194.sh on the committed data"
