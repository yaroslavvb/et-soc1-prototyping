#!/usr/bin/env bash
# E189 (Q167, the kit), the box step "the release, then the collection" (this file is s22): after the card lane's release (the day's post
# ' — released'), E189's session directory copied back READ-ONLY from aifoundry3 and turned into the data directory at the desk. E188's
# step 11's form (tools/claims-v3/e188/rb/s22_collect_e188.sh): the T0 the runbook launched (RB_OUT/e189-T0.txt); the box read first (the
# session ended, its MANIFEST.sha256 written, no session of ours still running, the box's home path for the scrub); ONE bounded rsync
# from the box into RB_OUT/e189-raw/T<T0>/ (a copy: nothing on the box is moved or removed); then collect_e189.py at the desk:
# COPY-BACK EXACT, the data directory docs/reports/data/<the window's day>-e189-blind-day-aifoundry3/ in E189.md 8.1's form, each pass
# reduced by energy_reduce.py UNCHANGED, the scrub, SHA256SUMS; then the desk-path gate (nopath_q142s.py) and the history check. A session
# that stopped at a gate is collected the same way (E184's lesson). The scorer is NOT run here: commit the data directory first (through
# commit_lab.sh), then s24_score_e189.sh.
#   bash tools/claims-v3/e189/rb/s22_collect_e189.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e189.sh"
rb_init s22_collect
e189_window
t0=; [ -f "$RB_OUT/e189-T0.txt" ] && t0=$(cat "$RB_OUT/e189-T0.txt")
[ -n "${RB_DRY:-}" ] && t0=${t0:-1794600000}
[ -n "$t0" ] || rb_die $RB_E_USAGE "RB_OUT holds no e189-T0.txt: step 9 has not launched E189 from this RB_OUT"
DATA=docs/reports/data/${RB_DAY:-DAY}-e189-blind-day-aifoundry3
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_REPO/$DATA" ] || rb_die $RB_E_USAGE "$DATA exists already: never merge into an earlier copy"
rb_probe aifoundry3
f=$(rb_file ended)
{ rb_prelude aifoundry3
  echo "T0=$t0"
  cat <<'EOF2'
SD=build/e189/T$T0
[ -f "$SD/session.log" ] || { echo "REFUSED: no session directory $SD on $BOX"; exit 3; }
grep -q 'session end' "$SD/session.log" || { echo "REFUSED: $SD has no 'session end' yet: wait (step 10)"; exit 3; }
[ -s "$SD/MANIFEST.sha256" ] || { echo "REFUSED: $SD has no MANIFEST.sha256 yet: wait (step 10)"; exit 3; }
if pgrep -u "$(id -u)" -f 'session_e189\.sh' > /dev/null; then echo "REFUSED: session_e189.sh still runs"; exit 3; fi
echo "BOXHOME $HOME"
echo "FILES $(find "$SD" -type f | wc -l | tr -d ' ')"
EOF2
} > "$f"
rb_remote read aifoundry3 "the session ended, its manifest written, nothing of ours running" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the copy exited $RB_RC: nothing copied"
bh=$(rb_val '^BOXHOME ([^ ]+)$')          # (rb_val's sed takes no slash in its pattern)
case "$bh" in /*|DRY) ;; *) bh="" ;; esac
[ -n "${RB_DRY:-}" ] && bh=${bh:-/home/BOX}
[ -n "$bh" ] || rb_die $RB_E_FAIL "the box's home path did not come back: nothing copied"
mkdir -p "$RB_OUT/e189-raw"
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_OUT/e189-raw/T$t0" ] || rb_die $RB_E_USAGE "RB_OUT/e189-raw/T$t0 exists already: never merge into an earlier copy (a new RB_OUT, or move it aside)"
rb_need_end 600
rb_probe aifoundry3
rb_local copy aifoundry3 "the session directory, copied from the box (read-only there)" rsync -a -e "$RB_RSH" "aifoundry3:aifoundry/build/e189/T$t0/" "$RB_OUT/e189-raw/T$t0/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy exited $RB_RC: run this step again (into a new RB_OUT/e189-raw, after moving the partial one aside)"
rb_local desk local "COPY-BACK EXACT, the data directory, the reducer (unchanged), the scrub, SHA256SUMS (collect_e189.py)" \
  /usr/bin/python3 -B tools/claims-v3/e189/collect_e189.py "$RB_OUT/e189-raw/T$t0" "$DATA" --box-home "$bh"
[ -n "${RB_DRY:-}" ] || rb_has '^COLLECTED ' || rb_die $RB_E_GATE "the collection did not read COLLECTED (the lines above): commit nothing"
rb_nopath "$RB_REPO/$DATA"
rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e189/rb/check_history_e189.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed after the collection"
rb_say "collected $DATA: commit it through commit_lab.sh (new files only), then run s24_score_e189.sh on the committed data"
